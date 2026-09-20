#!/usr/bin/env python3
"""Local canonical records for the agile-flow Codex plugin.

The program validates durable record relationships. It deliberately does not
claim that an external test, authorization, or user acceptance is genuine.
"""
from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import json
import os
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
DEVELOPMENT = {"pending", "preparing", "ready", "in_progress", "implemented", "canceled"}
VERIFY = {"not_run", "partial", "failed", "passed"}
ACCEPT = {"not_requested", "pending", "changes_requested", "accepted"}
RESULTS = {"passed", "failed", "not_run"}


class RecordError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode()).hexdigest()


def state_fingerprint(state: dict[str, Any]) -> str:
    body = copy.deepcopy(state)
    body.pop("integrity", None)
    return digest(body)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def response(status: str, **values: Any) -> dict[str, Any]:
    return {"status": status, **values}


class Store:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.directory = self.root / ".agile-flow"
        self.path = self.directory / "state.json"
        self.backup = self.directory / "state.backup.json"
        self.lock_path = self.directory / ".lock"
        self.views = self.directory / "views"
        self.view_manifest = self.views / ".manifest.json"

    def read(self) -> dict[str, Any]:
        if not self.path.exists():
            raise RecordError("No managed project exists at this root. Run initialize first.")
        try:
            state = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise RecordError(f"Canonical state is invalid JSON: {error}. Recovery requires an explicit restore.") from error
        self.validate(state)
        integrity = state.get("integrity", {})
        if integrity.get("fingerprint") != state_fingerprint(state):
            raise RecordError("Manual canonical-state edit detected. Preserve and reconcile it before mutation.")
        return state

    def validate(self, state: dict[str, Any]) -> None:
        if state.get("schema_version") != SCHEMA_VERSION:
            raise RecordError("Unsupported state schema version.")
        if not isinstance(state.get("revision"), int) or state["revision"] < 1:
            raise RecordError("State revision is invalid.")
        if not isinstance(state.get("project"), dict) or not state["project"].get("id"):
            raise RecordError("Project identity is missing.")
        ids: set[str] = set()
        for key, prefix in (("backlog", "ITEM-"), ("increments", "INC-"), ("decisions", "DEC-"),
                            ("evidence", "EVD-"), ("reviews", "REV-"), ("blockers", "BLK-"),
                            ("improvements", "IMP-")):
            for item in state.get(key, []):
                identifier = item.get("id")
                if not isinstance(identifier, str) or not identifier.startswith(prefix) or identifier in ids:
                    raise RecordError(f"Invalid or duplicate record identifier in {key}.")
                ids.add(identifier)
        increment_ids = {item["id"] for item in state.get("increments", [])}
        auth_ids = {item["id"] for item in state.get("decisions", [])}
        active = 0
        for inc in state.get("increments", []):
            states = inc.get("states", {})
            if states.get("development") not in DEVELOPMENT or states.get("verification") not in VERIFY or states.get("acceptance") not in ACCEPT:
                raise RecordError(f"Invalid work states on {inc['id']}.")
            if states["development"] == "in_progress" and not inc.get("suspended", False):
                active += 1
            if inc.get("authorization") and inc["authorization"] not in auth_ids:
                raise RecordError(f"Increment {inc['id']} references missing authorization.")
            if not set(inc.get("item_ids", [])).issubset({item["id"] for item in state.get("backlog", [])}):
                raise RecordError(f"Increment {inc['id']} references missing backlog work.")
        if active > 1:
            raise RecordError("At most one unsuspended increment may be in progress.")
        for item in state.get("evidence", []):
            if item.get("increment_id") not in increment_ids or item.get("result") not in RESULTS:
                raise RecordError("Evidence has an invalid increment or result.")

    def check_views(self) -> None:
        if not self.view_manifest.exists():
            return
        try:
            manifest = json.loads(self.view_manifest.read_text(encoding="utf-8"))
        except Exception as error:
            raise RecordError(f"Generated-view manifest is unreadable: {error}") from error
        changed = []
        for relative, expected in manifest.get("files", {}).items():
            path = self.views / relative
            if not path.exists() or file_hash(path) != expected:
                changed.append(relative)
        if changed:
            raise RecordError("Manual generated-view edit detected; reconcile or force a preserved regeneration: " + ", ".join(changed))

    def write(self, state: dict[str, Any]) -> None:
        state["integrity"] = {"fingerprint": state_fingerprint(state), "written_at": utc_now()}
        self.validate(state)
        self.directory.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            shutil.copy2(self.path, self.backup)
        fd, temp_name = tempfile.mkstemp(prefix="state.", suffix=".tmp", dir=self.directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(state, handle, ensure_ascii=False, indent=2, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def transaction(self, request: dict[str, Any]) -> dict[str, Any]:
        operation_id = request.get("operation_id")
        if not isinstance(operation_id, str) or not operation_id.strip():
            return response("failed", errors=["Mutation needs a non-empty operation_id."])
        self.directory.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                if request["operation"] == "initialize" and not self.path.exists():
                    state = initial_state(self.root, request)
                    self.write(state)
                    return response("applied", revision=state["revision"], fingerprint=state_fingerprint(state))
                state = self.read()
                existing = next((entry for entry in state["history"] if entry["operation_id"] == operation_id), None)
                request_digest = digest({key: value for key, value in request.items() if key not in {"expected_fingerprint", "expected_revision"}})
                if existing:
                    if existing["request_digest"] == request_digest:
                        return response("already_applied", revision=existing["result_revision"], fingerprint=existing["result_fingerprint"])
                    return response("conflict", errors=["Operation ID was already used with different content."])
                if request.get("expected_revision") != state["revision"] or request.get("expected_fingerprint") != state_fingerprint(state):
                    return response("conflict", revision=state["revision"], fingerprint=state_fingerprint(state), errors=["Expected revision or fingerprint is stale."])
                self.check_views()
                mutate(state, request, self.root)
                state["revision"] += 1
                state["history"].append({"operation_id": operation_id, "operation": request["operation"], "purpose": request.get("purpose", ""), "at": utc_now(), "request_digest": request_digest, "result_revision": state["revision"], "result_fingerprint": "pending"})
                future_fp = state_fingerprint(state)
                state["history"][-1]["result_fingerprint"] = future_fp
                self.write(state)
                return response("applied", revision=state["revision"], fingerprint=state_fingerprint(state))
            except RecordError as error:
                return response("failed", errors=[str(error)])
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)


def initial_state(root: Path, request: dict[str, Any]) -> dict[str, Any]:
    project = request.get("project", {})
    if not project.get("name") or not project.get("purpose"):
        raise RecordError("Initialize requires project.name and project.purpose.")
    now = utc_now()
    state = {"schema_version": SCHEMA_VERSION, "revision": 1,
             "project": {"id": str(uuid.uuid4()), "name": project["name"], "purpose": project["purpose"],
                         "root": str(root), "constraints": project.get("constraints", []), "references": project.get("references", []),
                         "administrative_state": "open", "next_step": project.get("next_step", "Refine the highest-value need.")},
             "quality_policy": request.get("quality_policy", []), "backlog": [], "increments": [], "decisions": [], "evidence": [],
             "reviews": [], "blockers": [], "improvements": [], "history": []}
    state["history"].append({"operation_id": request["operation_id"], "operation": "initialize", "purpose": request.get("purpose", "Initialize managed project."), "at": now, "request_digest": digest({key: value for key, value in request.items() if key not in {"expected_fingerprint", "expected_revision"}}), "result_revision": 1, "result_fingerprint": "pending"})
    state["history"][-1]["result_fingerprint"] = state_fingerprint(state)
    return state


def find(items: list[dict[str, Any]], identifier: str, label: str) -> dict[str, Any]:
    item = next((entry for entry in items if entry["id"] == identifier), None)
    if item is None:
        raise RecordError(f"Unknown {label}: {identifier}.")
    return item


def new_id(state: dict[str, Any], collection: str, prefix: str) -> str:
    return f"{prefix}-{len(state[collection]) + 1:04d}"


def recompute_verification(state: dict[str, Any], inc: dict[str, Any]) -> None:
    current = [ev for ev in state["evidence"] if ev["increment_id"] == inc["id"] and ev["delivery_revision"] == inc["delivery_revision"]]
    checks = inc.get("required_checks", [])
    results = {ev["check"]: ev["result"] for ev in current}
    if any(results.get(check) == "failed" for check in checks): value = "failed"
    elif checks and all(results.get(check) == "passed" for check in checks): value = "passed"
    elif any(result == "passed" for result in results.values()): value = "partial"
    else: value = "not_run"
    inc["states"]["verification"] = value


def mutate(state: dict[str, Any], request: dict[str, Any], root: Path) -> None:
    op = request["operation"]
    if op == "initialize":
        raise RecordError("This root is already initialized; initialization is retrieval, not duplication.")
    if op == "update-backlog":
        data = request.get("item", {})
        purpose = data.get("purpose")
        if not purpose: raise RecordError("Backlog item needs purpose.")
        matches = [item for item in state["backlog"] if item["purpose"].casefold() == purpose.casefold()]
        if matches and not data.get("id"):
            raise RecordError(f"Potential duplicate of {matches[0]['id']}; update it explicitly or resolve the ambiguity.")
        item = find(state["backlog"], data["id"], "backlog item") if data.get("id") else {"id": new_id(state, "backlog", "ITEM"), "state": "open", "created_at": utc_now()}
        if not data.get("id"): state["backlog"].append(item)
        item.update({key: data[key] for key in ("purpose", "type", "priority", "dependencies", "criteria", "uncertainties", "provenance") if key in data})
        item.setdefault("type", "feature"); item.setdefault("priority", {"value": "proposed", "basis": "Not yet decided."}); item.setdefault("provenance", {})
        item["updated_at"] = utc_now(); item["change_reason"] = request.get("purpose", "Backlog refinement.")
    elif op == "record-decision":
        data = request.get("decision", {})
        for key in ("author", "reason", "scope"):
            if not data.get(key): raise RecordError(f"Decision needs {key}.")
        state["decisions"].append({"id": new_id(state, "decisions", "DEC"), "at": utc_now(), **data})
    elif op == "prepare":
        data = request.get("increment", {})
        for key in ("objective", "scope", "criteria", "required_checks", "authorization"):
            if not data.get(key): raise RecordError(f"Preparation needs {key}.")
        if data["authorization"] not in {d["id"] for d in state["decisions"]}: raise RecordError("Preparation requires a recorded authorization decision.")
        if not set(data.get("item_ids", [])).issubset({item["id"] for item in state["backlog"]}): raise RecordError("Preparation references unknown backlog work.")
        state["increments"].append({"id": new_id(state, "increments", "INC"), "item_ids": data.get("item_ids", []), "objective": data["objective"], "scope": data["scope"], "exclusions": data.get("exclusions", []), "technical_plan": data.get("technical_plan", ""), "criteria": data["criteria"], "required_checks": data["required_checks"], "authorization": data["authorization"], "uncertainties": data.get("uncertainties", []), "states": {"development": "ready", "verification": "not_run", "acceptance": "not_requested"}, "delivery_revision": 1, "suspended": False, "created_at": utc_now()})
    elif op == "start":
        inc = find(state["increments"], request.get("increment_id", ""), "increment")
        if inc["states"]["development"] != "ready" or not inc.get("authorization"): raise RecordError("Only a ready, authorized increment can start.")
        if any(i["states"]["development"] == "in_progress" and not i.get("suspended") for i in state["increments"]): raise RecordError("Another increment is already in progress.")
        inc["states"]["development"] = "in_progress"; inc["suspended"] = False
    elif op == "mark-implemented":
        inc = find(state["increments"], request.get("increment_id", ""), "increment")
        if inc["states"]["development"] not in {"in_progress", "ready"}: raise RecordError("Increment is not ready for implementation completion.")
        inc["states"]["development"] = "implemented"; inc["states"]["acceptance"] = "pending"
        inc["baseline"] = request.get("baseline", {})
    elif op == "record-evidence":
        data = request.get("evidence", {}); inc = find(state["increments"], data.get("increment_id", ""), "increment")
        for key in ("check", "result", "scope"):
            if not data.get(key): raise RecordError(f"Evidence needs {key}.")
        if data["result"] not in RESULTS: raise RecordError("Evidence result is invalid.")
        if data["check"] not in inc["required_checks"]: raise RecordError("Evidence check is not required by this increment.")
        state["evidence"].append({"id": new_id(state, "evidence", "EVD"), "at": utc_now(), "delivery_revision": inc["delivery_revision"], "limitations": data.get("limitations", ""), "fingerprints": data.get("fingerprints", {}), "environment": data.get("environment", {}), **data})
        recompute_verification(state, inc)
    elif op == "record-review":
        data = request.get("review", {}); inc = find(state["increments"], data.get("increment_id", ""), "increment")
        if data.get("decision") not in {"accepted", "changes_requested", "deferred", "partial"}: raise RecordError("Review needs a valid explicit decision.")
        if not data.get("user_quote") and not data.get("message_reference"): raise RecordError("Review needs a verbatim user quote or message reference.")
        state["reviews"].append({"id": new_id(state, "reviews", "REV"), "at": utc_now(), "delivery_revision": inc["delivery_revision"], **data})
        inc["states"]["acceptance"] = "accepted" if data["decision"] == "accepted" else ("changes_requested" if data["decision"] in {"changes_requested", "partial"} else "pending")
    elif op == "record-blocker":
        data = request.get("blocker", {}); find(state["increments"], data.get("increment_id", ""), "increment")
        for key in ("condition", "resolution_requirement"):
            if not data.get(key): raise RecordError(f"Blocker needs {key}.")
        state["blockers"].append({"id": new_id(state, "blockers", "BLK"), "at": utc_now(), "state": "open", "attempts": data.get("attempts", []), **data})
    elif op == "record-improvement":
        data = request.get("improvement", {})
        for key in ("observation", "adjustment", "target_cycle"):
            if not data.get(key): raise RecordError(f"Improvement needs {key}.")
        state["improvements"].append({"id": new_id(state, "improvements", "IMP"), "at": utc_now(), "effect_evidence": data.get("effect_evidence", "Insufficient evidence."), **data})
    elif op == "mark-delivery-change":
        inc = find(state["increments"], request.get("increment_id", ""), "increment")
        if not request.get("reason"): raise RecordError("A behavior-affecting delivery change needs a reason.")
        inc["delivery_revision"] += 1; inc["states"]["verification"] = "not_run"; inc["states"]["acceptance"] = "pending"; inc["delivery_change_reason"] = request["reason"]
    elif op in {"pause", "close", "reopen"}:
        target = request.get("target", "increment"); action = request.get("action", op)
        if target == "project":
            if action == "pause": state["project"]["administrative_state"] = "paused"
            elif action == "close": state["project"]["administrative_state"] = "closed"
            elif action == "reopen": state["project"]["administrative_state"] = "open"
            else: raise RecordError("Invalid administrative action.")
        else:
            inc = find(state["increments"], request.get("increment_id", ""), "increment")
            if action == "pause": inc["suspended"] = True; inc["resumption_point"] = request.get("resumption_point", "Resume from recorded state.")
            elif action == "close": inc["administrative_state"] = "closed"
            elif action == "reopen": inc["administrative_state"] = "open"; inc["suspended"] = False
            else: raise RecordError("Invalid administrative action.")
    else:
        raise RecordError(f"Unsupported operation: {op}.")


def render(store: Store, force: bool) -> dict[str, Any]:
    state = store.read()
    if force and store.view_manifest.exists():
        changed = []
        manifest = json.loads(store.view_manifest.read_text(encoding="utf-8"))
        for relative, expected in manifest.get("files", {}).items():
            path = store.views / relative
            if path.exists() and file_hash(path) != expected:
                backup = path.with_name(path.name + ".manual-backup")
                shutil.copy2(path, backup); changed.append(str(backup.relative_to(store.directory)))
    else:
        store.check_views()
    store.views.mkdir(parents=True, exist_ok=True); (store.views / "increments").mkdir(exist_ok=True)
    active = next((i for i in state["increments"] if i["states"]["development"] == "in_progress" and not i.get("suspended")), None)
    summary = ["# agile-flow summary", "", f"Generated from canonical revision {state['revision']}.", "", f"Project: {state['project']['name']}", f"Objective: {state['project']['purpose']}", f"Next step: {state['project']['next_step']}", f"Active increment: {active['id'] if active else 'None'}"]
    backlog = ["# Backlog", "", f"Generated from canonical revision {state['revision']}.", ""] + [f"- {item['id']}: {item['purpose']} ({item.get('priority', {}).get('value', 'proposed')})" for item in state["backlog"]]
    files = {"summary.md": "\n".join(summary) + "\n", "backlog.md": "\n".join(backlog) + "\n"}
    for inc in state["increments"]:
        lines = [f"# {inc['id']}: {inc['objective']}", "", f"Generated from canonical revision {state['revision']}.", "", f"Development: {inc['states']['development']}", f"Verification: {inc['states']['verification']}", f"Acceptance: {inc['states']['acceptance']}", "", "## Scope", inc['scope'], "", "## Criteria"] + [f"- {criterion}" for criterion in inc['criteria']]
        files[f"increments/{inc['id']}.md"] = "\n".join(lines) + "\n"
    for relative, content in files.items():
        (store.views / relative).write_text(content, encoding="utf-8")
    manifest = {"source_revision": state["revision"], "files": {relative: file_hash(store.views / relative) for relative in files}}
    store.view_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return response("applied", revision=state["revision"], generated=list(files))


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage local agile-flow records.")
    parser.add_argument("--root", default=".", help="Product root; defaults to the current directory.")
    parser.add_argument("--request", help="JSON request file; omit to read JSON from standard input.")
    parser.add_argument("command", choices=["inspect", "validate", "mutate", "render", "recover"])
    parser.add_argument("--force", action="store_true", help="Preserve manually edited views and regenerate them.")
    args = parser.parse_args(); store = Store(Path(args.root))
    try:
        if args.command == "inspect":
            state = store.read(); print(json.dumps(response("ok", revision=state["revision"], fingerprint=state_fingerprint(state), project=state["project"], backlog=state["backlog"], decisions=state["decisions"], increments=state["increments"], blockers=[b for b in state["blockers"] if b["state"] == "open"], improvements=state["improvements"]), ensure_ascii=False, indent=2)); return
        if args.command == "validate":
            state = store.read(); store.check_views(); print(json.dumps(response("ok", revision=state["revision"]), indent=2)); return
        if args.command == "render": print(json.dumps(render(store, args.force), indent=2)); return
        if args.command == "recover":
            if not store.backup.exists(): raise RecordError("No backup is available for explicit recovery.")
            backup = json.loads(store.backup.read_text(encoding="utf-8")); store.validate(backup)
            corrupted = store.path.with_name("state.corrupt.json")
            if store.path.exists(): shutil.move(store.path, corrupted)
            store.write(backup); print(json.dumps(response("applied", recovered_from=str(store.backup), preserved_corrupt=str(corrupted)), indent=2)); return
        raw = Path(args.request).read_text(encoding="utf-8") if args.request else sys.stdin.read()
        request = json.loads(raw)
        if not isinstance(request, dict) or "operation" not in request: raise RecordError("Request must be a JSON object with operation.")
        print(json.dumps(store.transaction(request), ensure_ascii=False, indent=2))
    except (RecordError, OSError, json.JSONDecodeError) as error:
        print(json.dumps(response("failed", errors=[str(error)]), ensure_ascii=False, indent=2)); sys.exit(1)


if __name__ == "__main__":
    main()
