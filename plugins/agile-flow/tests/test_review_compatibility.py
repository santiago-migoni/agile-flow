"""Review compatibility behavior of the shared lifecycle engine."""
import unittest
import json
from scripts.legacy_records import state_fingerprint
from record_scenarios import DeliveredRecordsHarness


class ReviewCompatibilityTests(DeliveredRecordsHarness, unittest.TestCase):
    def test_legacy_review_without_binding_remains_readable_and_conservative(self):
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Start", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-implemented", "operation_id": "implemented", "purpose": "Deliver", "increment_id": "INC-0001"})
        covered = self.root / "app.py"
        covered.write_text("first\n")
        self.mutate({"operation": "record-evidence", "operation_id": "old-unit", "purpose": "Initial unit check", "evidence": {"increment_id": "INC-0001", "check": "unit", "result": "passed", "scope": "app.py", "paths": ["app.py"]}})
        self.mutate({"operation": "record-review", "operation_id": "old-review", "purpose": "Initial acceptance", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "Accepted."}})
        state_path = self.root / ".agile-flow" / "state.json"
        state = json.loads(state_path.read_text())
        state["reviews"][0].pop("evidence_ids")
        state["reviews"][0].pop("reviewed_fingerprints")
        state["integrity"]["fingerprint"] = state_fingerprint(state)
        state_path.write_text(json.dumps(state))
        self.assertEqual(self.inspect()["increments"][0]["effective_acceptance"], "accepted")
        self.mutate({"operation": "record-evidence", "operation_id": "legacy-later-manual", "purpose": "Later check after legacy review", "evidence": {"increment_id": "INC-0001", "check": "manual", "result": "passed", "scope": "app.py", "paths": ["app.py"]}})
        self.assertEqual(self.inspect()["increments"][0]["effective_acceptance"], "accepted")
        covered.write_text("second\n")
        self.assertEqual(self.inspect()["increments"][0]["effective_acceptance"], "pending")

    def test_legacy_review_without_reconstructible_history_is_pending(self):
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Start", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-implemented", "operation_id": "implemented", "purpose": "Deliver", "increment_id": "INC-0001"})
        self.mutate({"operation": "record-evidence", "operation_id": "unit", "purpose": "Run unit check", "evidence": {"increment_id": "INC-0001", "check": "unit", "result": "passed", "scope": "Greeting"}})
        self.mutate({"operation": "record-review", "operation_id": "accept", "purpose": "Accept", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "Accepted."}})
        state_path = self.root / ".agile-flow" / "state.json"
        state = json.loads(state_path.read_text())
        state["reviews"][0].pop("evidence_ids")
        state["reviews"][0].pop("reviewed_fingerprints")
        state["history"] = []
        state["integrity"]["fingerprint"] = state_fingerprint(state)
        state_path.write_text(json.dumps(state))
        self.assertEqual(self.inspect()["increments"][0]["effective_acceptance"], "pending")
