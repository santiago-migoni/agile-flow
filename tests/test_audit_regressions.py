from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from test_records import RecordsHarness


class AuditRegressions(RecordsHarness, unittest.TestCase):
    def test_a01_stale_review_cannot_accept_current_delivery_and_partial_parts_accumulate(self):
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Begin", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-implemented", "operation_id": "done", "purpose": "Deliver", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-delivery-change", "operation_id": "change", "purpose": "Change", "increment_id": "INC-0001", "reason": "Behavior changed."})
        self.mutate({"operation": "record-review", "operation_id": "old-review", "purpose": "Historical acceptance", "review": {"increment_id": "INC-0001", "delivery_revision": 1, "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "I accepted the first version."}})
        current = self.inspect()
        self.assertNotEqual(current["increments"][0]["states"]["acceptance"], "accepted")
        self.assertEqual(current["reviews"][0]["delivery_revision"], 1)
        self.mutate({"operation": "record-review", "operation_id": "partial", "purpose": "Partial acceptance", "review": {"increment_id": "INC-0001", "delivery_revision": 2, "decision": "partial", "accepted_parts": ["Returns greeting"], "user_quote": "This part is accepted."}})
        self.assertEqual(self.inspect()["increments"][0]["states"]["acceptance"], "pending")
        self.mutate({"operation": "record-review", "operation_id": "explicit", "purpose": "Complete acceptance", "review": {"increment_id": "INC-0001", "delivery_revision": 2, "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "I accept this delivery."}})
        self.assertEqual(self.inspect()["increments"][0]["states"]["acceptance"], "accepted")

    def test_partial_acceptance_identifies_parts_without_accepting_whole(self):
        self.initialize(); self.backlog(); self.authorization()
        self.mutate({"operation": "prepare", "operation_id": "two-parts", "purpose": "Prepare two parts", "increment": {"item_ids": ["ITEM-0001"], "objective": "Greeting and label", "scope": "Response", "criteria": ["Returns greeting", "Shows correct label"], "required_checks": ["unit"], "authorization": "DEC-0001"}})
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Begin", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-implemented", "operation_id": "done", "purpose": "Deliver", "increment_id": "INC-0001"})
        self.mutate({"operation": "record-review", "operation_id": "part", "purpose": "Review greeting", "review": {"increment_id": "INC-0001", "decision": "partial", "accepted_parts": ["Returns greeting"], "user_quote": "The greeting is good; I have not reviewed the label."}})
        inc = self.inspect()["increments"][0]
        self.assertEqual(inc["accepted_parts"], ["Returns greeting"])
        self.assertEqual(inc["states"]["acceptance"], "pending")
        self.mutate({"operation": "record-review", "operation_id": "other", "purpose": "Review label", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Shows correct label"], "user_quote": "The label is accepted."}})
        self.assertEqual(self.inspect()["increments"][0]["states"]["acceptance"], "accepted")

    def test_a02_correction_cycle_and_a05_lifecycle(self):
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Begin", "increment_id": "INC-0001"})
        self.mutate({"operation": "record-blocker", "operation_id": "block", "purpose": "Blocked manual check", "blocker": {"increment_id": "INC-0001", "condition": "Credential missing", "resolution_requirement": "Credential available"}})
        self.mutate({"operation": "mark-implemented", "operation_id": "done", "purpose": "Deliver", "increment_id": "INC-0001"})
        self.mutate({"operation": "record-review", "operation_id": "changes", "purpose": "Correction requested", "review": {"increment_id": "INC-0001", "decision": "changes_requested", "requested_changes": ["Correct the label"], "user_quote": "Correct the label."}})
        self.mutate({"operation": "prepare-correction", "operation_id": "correct", "purpose": "Prepare correction", "increment_id": "INC-0001", "reason": "Address the label correction."})
        self.assertEqual(self.inspect()["increments"][0]["delivery_revision"], 2)
        self.mutate({"operation": "start", "operation_id": "restart", "purpose": "Apply correction", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-implemented", "operation_id": "redone", "purpose": "Corrected", "increment_id": "INC-0001"})
        self.mutate({"operation": "resolve-blocker", "operation_id": "unblock", "purpose": "Credential supplied", "blocker_id": "BLK-0001", "resolution": "Credential was supplied and check ran."})
        for check in ("unit", "manual"):
            self.mutate({"operation": "record-evidence", "operation_id": "check-" + check, "purpose": "Run check", "evidence": {"increment_id": "INC-0001", "check": check, "result": "passed", "scope": "Greeting endpoint"}})
        self.mutate({"operation": "record-review", "operation_id": "accept", "purpose": "Accept correction", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "The corrected delivery is accepted."}})
        self.mutate({"operation": "complete-backlog", "operation_id": "complete", "purpose": "Complete need", "item_id": "ITEM-0001", "reason": "Current delivery is implemented, passed, and accepted."})
        self.mutate({"operation": "record-improvement", "operation_id": "improve", "purpose": "Apply learning", "improvement": {"observation": "Label ambiguity caused rework.", "adjustment": "Add label examples.", "target_cycle": "Next increment"}})
        self.mutate({"operation": "follow-up-improvement", "operation_id": "follow", "purpose": "Evaluate learning", "improvement_id": "IMP-0001", "state": "applied", "effect_evidence": "Next criteria include label examples."})
        self.mutate({"operation": "update-project", "operation_id": "next", "purpose": "Update next step", "project": {"next_step": "Select the next authorized item."}})
        state = self.inspect()
        self.assertEqual(state["increments"][0]["states"], {"development": "implemented", "verification": "passed", "acceptance": "accepted"})
        self.assertEqual(state["blockers"][0]["state"], "resolved")
        self.assertEqual(state["improvements"][0]["state"], "applied")
        self.assertEqual(state["backlog"][0]["state"], "completed")
        self.assertEqual(state["project"]["next_step"], "Select the next authorized item.")

    def test_a03_technical_and_superseded_decisions_do_not_authorize(self):
        self.initialize(); self.backlog()
        self.mutate({"operation": "record-decision", "operation_id": "tech", "purpose": "Technical choice", "decision": {"kind": "technical", "author": "agent", "reason": "Use Python", "scope": "Implementation", "source": "local analysis"}})
        payload = {"operation": "prepare", "operation_id": "bad", "purpose": "Prepare", "increment": {"item_ids": ["ITEM-0001"], "objective": "Greeting", "scope": "Greeting endpoint", "criteria": ["Returns greeting"], "required_checks": ["unit"], "authorization": "DEC-0001"}}
        self.assertEqual(self.mutate(payload)["status"], "failed")
        self.mutate({"operation": "record-decision", "operation_id": "unrelated-auth", "purpose": "Authorize unrelated work", "decision": {"kind": "authorization", "author": "user", "reason": "Different request", "scope": {"item_ids": ["ITEM-9999"]}, "source": "message", "quote": "Build a different item."}})
        payload["operation_id"] = "unrelated"; payload["increment"]["authorization"] = "DEC-0002"
        payload.pop("expected_revision"); payload.pop("expected_fingerprint")
        self.assertEqual(self.mutate(payload)["status"], "failed")
        self.mutate({"operation": "record-decision", "operation_id": "auth", "purpose": "Authorize", "decision": {"kind": "authorization", "author": "user", "reason": "Requested feature", "scope": {"item_ids": ["ITEM-0001"]}, "source": "message", "quote": "Build the greeting."}})
        self.mutate({"operation": "record-decision", "operation_id": "supersede", "purpose": "Revoke", "decision": {"kind": "revocation", "author": "user", "reason": "Changed direction", "scope": {"item_ids": ["ITEM-0001"]}, "source": "message", "supersedes": ["DEC-0003"]}})
        payload["operation_id"] = "revoked"; payload["increment"]["authorization"] = "DEC-0003"
        payload.pop("expected_revision"); payload.pop("expected_fingerprint")
        self.assertEqual(self.mutate(payload)["status"], "failed")

    def test_a04_history_keeps_multiple_prior_values_and_provenance(self):
        self.initialize(); self.backlog()
        for number, purpose in enumerate(("Revised need", "Final need"), 1):
            self.mutate({"operation": "update-backlog", "operation_id": f"update-{number}", "purpose": f"Revision {number}", "provenance": {"source": "user message"}, "item": {"id": "ITEM-0001", "purpose": purpose}})
        changes = [entry for entry in self.inspect()["history"] if entry["operation"] == "update-backlog"]
        self.assertEqual([entry["changes"][0]["before"]["purpose"] for entry in changes[1:]], ["Show a greeting.", "Revised need"])
        self.assertEqual(changes[-1]["provenance"]["source"], "user message")

    def test_a06_replay_metadata_matches_committed_state(self):
        initialized = self.initialize()
        request = {"operation": "initialize", "operation_id": "op-init", "purpose": "Create a test project.", "project": {"name": "Test", "purpose": "Verify records."}}
        _, replay = self.call("mutate", request)
        self.assertEqual((replay["revision"], replay["fingerprint"]), (initialized["revision"], initialized["fingerprint"]))
        applied = self.mutate({"operation": "record-decision", "operation_id": "decision", "purpose": "Technical choice", "decision": {"kind": "technical", "author": "agent", "reason": "Simple", "scope": "Project", "source": "local analysis"}})
        _, replay = self.call("mutate", {"operation": "record-decision", "operation_id": "decision", "purpose": "Technical choice", "decision": {"kind": "technical", "author": "agent", "reason": "Simple", "scope": "Project", "source": "local analysis"}})
        self.assertEqual((applied["revision"], applied["fingerprint"]), (replay["revision"], replay["fingerprint"]))

    def test_a07_invalid_backup_is_rejected_and_snapshots_are_unique(self):
        self.initialize(); self.backlog()
        backup = self.root / ".agile-flow" / "state.backup.json"
        data = json.loads(backup.read_text()); data["project"]["name"] = "Tampered"; backup.write_text(json.dumps(data))
        _, result = self.call("recover")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(self.inspect()["project"]["name"], "Test")

    def test_changed_file_marks_current_evidence_stale_without_writing_state(self):
        self.prepared()
        path = self.root / "app.py"; path.write_text("print('first')\n")
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Begin", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-implemented", "operation_id": "done", "purpose": "Deliver", "increment_id": "INC-0001"})
        for check in ("unit", "manual"):
            self.mutate({"operation": "record-evidence", "operation_id": "ev-" + check, "purpose": "Check", "evidence": {"increment_id": "INC-0001", "check": check, "result": "passed", "scope": "app.py", "paths": ["app.py"]}})
        before = self.inspect(); self.assertEqual(before["increments"][0]["effective_verification"], "passed")
        path.write_text("print('second')\n")
        after = self.inspect()
        self.assertEqual(after["revision"], before["revision"])
        self.assertEqual(after["increments"][0]["effective_verification"], "not_run")
        self.assertEqual(after["stale_evidence"], ["EVD-0001", "EVD-0002"])

    def test_manual_reconciliation_preserves_original_snapshot(self):
        self.initialize()
        path = self.root / ".agile-flow" / "state.json"
        data = json.loads(path.read_text()); data["project"]["next_step"] = "Review the revised goal."
        path.write_text(json.dumps(data))
        raw_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        request = {"operation_id": "manual-review", "expected_raw_hash": raw_hash, "reason": "Reviewed the intentional context edit.", "reviewed_by": "user"}
        code, result = self.call("reconcile-manual", request)
        self.assertEqual((code, result["status"]), (0, "applied"))
        self.assertTrue(Path(result["preserved_snapshot"]).exists())
        self.assertEqual(self.inspect()["project"]["next_step"], "Review the revised goal.")
        _, replay = self.call("reconcile-manual", request)
        self.assertEqual((replay["status"], replay["fingerprint"]), ("already_applied", result["fingerprint"]))
