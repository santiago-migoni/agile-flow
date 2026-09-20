import unittest
from test_records import RecordsHarness


class TransitionTest(RecordsHarness, unittest.TestCase):
    def test_second_active_increment_is_rejected(self) -> None:
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "first-start", "purpose": "Start first", "increment_id": "INC-0001"})
        self.mutate({"operation": "update-backlog", "operation_id": "second-item", "purpose": "Second need", "item": {"purpose": "Show a farewell."}})
        self.mutate({"operation": "prepare", "operation_id": "second-prepare", "purpose": "Prepare second", "increment": {"item_ids": ["ITEM-0002"], "objective": "Deliver farewell.", "scope": "Farewell endpoint.", "criteria": ["Returns farewell"], "required_checks": ["unit"], "authorization": "DEC-0001"}})
        body = self.mutate({"operation": "start", "operation_id": "second-start", "purpose": "Start second", "increment_id": "INC-0002"})
        self.assertEqual(body["status"], "failed")

    def test_reusing_operation_id_with_different_content_conflicts(self) -> None:
        self.initialize()
        self.mutate({"operation": "record-decision", "operation_id": "same-id", "purpose": "First", "decision": {"author": "agent", "reason": "First", "scope": "First"}})
        current = self.inspect()
        _, body = self.call("mutate", {"operation": "record-decision", "operation_id": "same-id", "purpose": "Different", "expected_revision": current["revision"], "expected_fingerprint": current["fingerprint"], "decision": {"author": "agent", "reason": "Different", "scope": "Different"}})
        self.assertEqual(body["status"], "conflict")

    def test_missing_authorization_and_unavailable_check(self) -> None:
        self.initialize(); self.backlog()
        body = self.mutate({"operation": "prepare", "operation_id": "no-auth", "purpose": "x", "increment": {"item_ids": ["ITEM-0001"], "objective": "x", "scope": "x", "criteria": ["x"], "required_checks": ["external"], "authorization": "DEC-9999"}})
        self.assertEqual(body["status"], "failed")
        self.prepared()
        self.mutate({"operation": "record-blocker", "operation_id": "block", "purpose": "Credential unavailable", "blocker": {"increment_id": "INC-0001", "condition": "Credential missing.", "resolution_requirement": "Supply credential."}})
        self.assertEqual(self.inspect()["blockers"][0]["state"], "open")

    def test_pause_preserves_work_and_close_does_not_complete(self) -> None:
        self.prepared(); self.mutate({"operation": "start", "operation_id": "start", "purpose": "x", "increment_id": "INC-0001"})
        self.mutate({"operation": "pause", "operation_id": "pause", "purpose": "Urgent work", "increment_id": "INC-0001", "resumption_point": "Resume tests."})
        inc = self.inspect()["increments"][0]; self.assertTrue(inc["suspended"]); self.assertEqual(inc["states"]["development"], "in_progress")
        self.mutate({"operation": "close", "operation_id": "close", "purpose": "Administrative close", "increment_id": "INC-0001"})
        inc = self.inspect()["increments"][0]; self.assertEqual(inc["administrative_state"], "closed"); self.assertEqual(inc["states"]["verification"], "not_run")
