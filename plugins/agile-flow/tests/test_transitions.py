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
        self.mutate({"operation": "record-decision", "operation_id": "same-id", "purpose": "First", "decision": {"kind": "technical", "source": "local observation", "author": "agent", "reason": "First", "scope": "First"}})
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

    def test_project_pause_and_cancellation_stop_new_development(self) -> None:
        self.prepared()
        self.mutate({"operation": "pause", "operation_id": "pause-project", "purpose": "Pause", "target": "project"})
        blocked = self.mutate({"operation": "start", "operation_id": "blocked-start", "purpose": "Attempt start", "increment_id": "INC-0001"})
        self.assertEqual(blocked["status"], "failed")
        self.mutate({"operation": "reopen", "operation_id": "reopen-project", "purpose": "Resume project", "target": "project"})
        self.mutate({"operation": "close", "action": "cancel", "operation_id": "cancel-increment", "purpose": "Cancel work", "increment_id": "INC-0001"})
        self.assertEqual(self.inspect()["increments"][0]["states"]["development"], "canceled")
        self.mutate({"operation": "reopen", "operation_id": "reopen-increment", "purpose": "Restart canceled work", "increment_id": "INC-0001"})
        self.assertEqual(self.inspect()["increments"][0]["states"]["development"], "ready")

    def test_closed_unfinished_work_frees_slot_but_cannot_reopen_into_conflict(self):
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "first-start", "purpose": "Start first", "increment_id": "INC-0001"})
        self.mutate({"operation": "close", "operation_id": "first-close", "purpose": "Close unfinished work", "increment_id": "INC-0001"})
        first = self.inspect()["increments"][0]
        self.assertEqual((first["administrative_state"], first["states"]["development"]), ("closed", "in_progress"))
        self.assertIsNone(self.inspect()["active_increment"])
        self.mutate({"operation": "update-backlog", "operation_id": "second-item", "purpose": "Second need", "item": {"purpose": "Show a farewell."}})
        self.mutate({"operation": "prepare", "operation_id": "second-prepare", "purpose": "Prepare second", "increment": {"item_ids": ["ITEM-0002"], "objective": "Deliver farewell", "scope": "Farewell endpoint", "criteria": ["Returns farewell"], "required_checks": ["unit"], "authorization": "DEC-0001"}})
        self.assertEqual(self.mutate({"operation": "start", "operation_id": "second-start", "purpose": "Start second", "increment_id": "INC-0002"})["status"], "applied")
        self.assertEqual(self.inspect()["active_increment"], "INC-0002")
        view = (self.root / ".agile-flow" / "views" / "summary.md").read_text()
        self.assertIn("Active increment: INC-0002", view)
        self.assertIn("INC-0001: administrative closed; development in_progress; active no", view)
        self.assertEqual(self.mutate({"operation": "reopen", "operation_id": "first-reopen-blocked", "purpose": "Try to reopen first", "increment_id": "INC-0001"})["status"], "failed")
        self.assertEqual(self.inspect()["increments"][0]["administrative_state"], "closed")
        self.mutate({"operation": "pause", "operation_id": "second-pause", "purpose": "Suspend second", "increment_id": "INC-0002"})
        self.assertEqual(self.mutate({"operation": "reopen", "operation_id": "first-reopen", "purpose": "Reopen first", "increment_id": "INC-0001"})["status"], "applied")
        self.assertEqual(self.inspect()["active_increment"], "INC-0001")
        self.assertEqual(self.mutate({"operation": "resume", "operation_id": "second-resume-blocked", "purpose": "Try second", "increment_id": "INC-0002"})["status"], "failed")
