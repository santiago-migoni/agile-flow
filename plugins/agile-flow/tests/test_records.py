from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "agile_flow.py"


class RecordsHarness:
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "product"
        self.root.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def call(self, command: str, request: dict | None = None, extra: list[str] | None = None) -> tuple[int, dict]:
        args = [sys.executable, str(SCRIPT), "--root", str(self.root)]
        if extra: args.extend(extra)
        args.append(command)
        result = subprocess.run(args, input=json.dumps(request) if request else None, text=True, capture_output=True, check=False)
        return result.returncode, json.loads(result.stdout)

    def initialize(self) -> dict:
        code, body = self.call("mutate", {"operation": "initialize", "operation_id": "op-init", "purpose": "Create a test project.", "project": {"name": "Test", "purpose": "Verify records."}})
        self.assertEqual((code, body["status"]), (0, "applied"))
        return self.inspect()

    def inspect(self) -> dict:
        code, body = self.call("inspect")
        self.assertEqual((code, body["status"]), (0, "ok"))
        return body

    def mutate(self, payload: dict) -> dict:
        current = self.inspect()
        payload.setdefault("expected_revision", current["revision"])
        payload.setdefault("expected_fingerprint", current["fingerprint"])
        code, body = self.call("mutate", payload)
        self.assertEqual(code, 0, body)
        return body

    def authorization(self) -> str:
        body = self.mutate({"operation": "record-decision", "operation_id": "op-auth", "purpose": "Record authorization.", "decision": {"kind": "authorization", "author": "user", "reason": "Authorized the increment.", "scope": {"item_ids": ["ITEM-0001", "ITEM-0002"]}, "source": "message", "quote": "Build it."}})
        self.assertEqual(body["status"], "applied")
        return "DEC-0001"

    def backlog(self) -> str:
        body = self.mutate({"operation": "update-backlog", "operation_id": "op-item", "purpose": "Capture need.", "item": {"purpose": "Show a greeting.", "type": "feature", "priority": {"value": "high", "basis": "User decision."}, "provenance": {"source": "user"}}})
        self.assertEqual(body["status"], "applied")
        return "ITEM-0001"

    def prepared(self) -> str:
        if not (self.root / ".agile-flow" / "state.json").exists():
            self.initialize()
        if not self.inspect()["backlog"]:
            self.backlog()
        if not self.inspect().get("decisions"):
            self.authorization()
        body = self.mutate({"operation": "prepare", "operation_id": "op-prepare", "purpose": "Prepare greeting.", "increment": {"item_ids": ["ITEM-0001"], "objective": "Deliver greeting.", "scope": "Greeting endpoint.", "criteria": ["Returns greeting"], "required_checks": ["unit", "manual"], "authorization": "DEC-0001"}})
        self.assertEqual(body["status"], "applied")
        return "INC-0001"

    def check_initialize_is_idempotent_and_duplicate_need_is_visible(self) -> None:
        self.initialize()
        body = self.mutate({"operation": "initialize", "operation_id": "op-init-again", "purpose": "Again"})
        self.assertEqual(body["status"], "failed")
        self.backlog()
        body = self.mutate({"operation": "update-backlog", "operation_id": "op-duplicate", "purpose": "Duplicate", "item": {"purpose": "Show a greeting."}})
        self.assertEqual(body["status"], "failed")

    def check_idempotency_conflict_and_active_limit(self) -> None:
        self.prepared()
        body = self.mutate({"operation": "start", "operation_id": "op-start", "purpose": "Start", "increment_id": "INC-0001"})
        self.assertEqual(body["status"], "applied")
        repeated = {"operation": "start", "operation_id": "op-start", "purpose": "Start", "increment_id": "INC-0001", "expected_revision": 5, "expected_fingerprint": "ignored"}
        _, body = self.call("mutate", repeated)
        self.assertEqual(body["status"], "already_applied")
        state = self.inspect(); stale = {"operation": "record-decision", "operation_id": "op-stale", "purpose": "x", "expected_revision": 1, "expected_fingerprint": state["fingerprint"], "decision": {"author": "agent", "reason": "x", "scope": "x"}}
        _, body = self.call("mutate", stale); self.assertEqual(body["status"], "conflict")

    def check_verification_partial_acceptance_and_invalidation(self) -> None:
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "op-start", "purpose": "Start", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-implemented", "operation_id": "op-implemented", "purpose": "Implemented", "increment_id": "INC-0001", "baseline": {"files": {"app.py": "abc"}}})
        self.mutate({"operation": "record-evidence", "operation_id": "op-unit", "purpose": "Unit check", "evidence": {"increment_id": "INC-0001", "check": "unit", "result": "passed", "scope": "Greeting endpoint"}})
        self.assertEqual(self.inspect()["increments"][0]["states"]["verification"], "partial")
        self.mutate({"operation": "record-review", "operation_id": "op-review", "purpose": "Review", "review": {"increment_id": "INC-0001", "decision": "accepted", "user_quote": "I accept the greeting."}})
        self.assertEqual(self.inspect()["increments"][0]["states"]["acceptance"], "accepted")
        self.mutate({"operation": "mark-delivery-change", "operation_id": "op-change", "purpose": "Behavior changed", "increment_id": "INC-0001", "reason": "Greeting behavior changed."})
        states = self.inspect()["increments"][0]["states"]
        self.assertEqual((states["verification"], states["acceptance"]), ("not_run", "pending"))

    def check_view_edit_is_preserved_and_blocks_mutation(self) -> None:
        self.initialize(); code, rendered = self.call("render"); self.assertEqual((code, rendered["status"]), (0, "applied"))
        view = self.root / ".agile-flow" / "views" / "summary.md"; view.write_text("manual change\n", encoding="utf-8")
        body = self.mutate({"operation": "record-decision", "operation_id": "op-blocked", "purpose": "x", "decision": {"author": "agent", "reason": "x", "scope": "x"}})
        self.assertEqual(body["status"], "failed")
        code, rendered = self.call("render", extra=["--force"]); self.assertEqual((code, rendered["status"]), (0, "applied"))
        self.assertEqual(len(list(view.parent.glob("summary.md.manual-*.backup"))), 1)

    def check_manual_state_edit_and_explicit_recovery(self) -> None:
        self.initialize(); state = self.root / ".agile-flow" / "state.json"
        raw = json.loads(state.read_text()); raw["project"]["name"] = "Manual"; state.write_text(json.dumps(raw), encoding="utf-8")
        code, body = self.call("inspect"); self.assertNotEqual(code, 0); self.assertEqual(body["status"], "failed")
        # A valid backup is created only by a later successful canonical write.
        self.assertFalse((self.root / ".agile-flow" / "state.backup.json").exists())


class RecordProgramTests(RecordsHarness, unittest.TestCase):
    def test_initialize_is_idempotent_and_duplicate_need_is_visible(self): self.check_initialize_is_idempotent_and_duplicate_need_is_visible()
    def test_idempotency_conflict_and_active_limit(self): self.check_idempotency_conflict_and_active_limit()
    def test_verification_partial_acceptance_and_invalidation(self): self.check_verification_partial_acceptance_and_invalidation()
    def test_view_edit_is_preserved_and_blocks_mutation(self): self.check_view_edit_is_preserved_and_blocks_mutation()
    def test_manual_state_edit_and_explicit_recovery(self): self.check_manual_state_edit_and_explicit_recovery()
