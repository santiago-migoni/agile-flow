"""Correction workflow behavior of the shared lifecycle engine."""
import unittest

from record_scenarios import DeliveredRecordsHarness


class CorrectionWorkflowTests(DeliveredRecordsHarness, unittest.TestCase):
    def test_correction_cycle_and_lifecycle(self):
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

    def test_failed_check_reopens_same_increment_without_user_review(self):
        self.delivered()
        self.mutate({"operation": "record-evidence", "operation_id": "failed", "purpose": "Observed failure", "evidence": {"increment_id": "INC-0001", "check": "unit", "result": "failed", "scope": "Greeting endpoint"}})
        outcome = self.mutate({"operation": "prepare-correction", "operation_id": "technical-correction", "purpose": "Fix failed check", "increment_id": "INC-0001", "basis": "technical_failure", "evidence_ids": ["EVD-0001"], "reason": "Unit check failed."})
        self.assertEqual(outcome["status"], "applied")
        inc = self.inspect()["increments"][0]
        self.assertEqual((inc["id"], inc["delivery_revision"], inc["states"]["development"]), ("INC-0001", 2, "ready"))
        self.assertEqual(self.inspect()["reviews"], [])

    def test_full_replacement_technical_correction_and_review_cycle(self):
        self.delivered()
        self.mutate({"operation": "record-evidence", "operation_id": "failed-unit", "purpose": "Observe failure", "evidence": {"increment_id": "INC-0001", "check": "unit", "result": "failed", "scope": "Greeting endpoint"}})
        self.mutate({"operation": "record-review", "operation_id": "review-change", "purpose": "Review first delivery", "review": {"increment_id": "INC-0001", "decision": "changes_requested", "parts": ["Returns greeting"], "user_quote": "Correct the greeting."}})
        self.mutate({"operation": "record-decision", "operation_id": "replacement-cycle", "purpose": "Record replacement authorization", "decision": {"kind": "authorization", "author": "user", "reason": "Continue correction", "scope": {"increment_ids": ["INC-0001"]}, "source": "test user message", "supersedes": ["DEC-0001"]}})
        self.assertEqual(self.mutate({"operation": "prepare-correction", "operation_id": "blocked-old", "purpose": "Attempt under old grant", "increment_id": "INC-0001", "basis": "technical_failure", "evidence_ids": ["EVD-0001"], "reason": "Fix failed unit check"})["status"], "failed")
        self.mutate({"operation": "rebind-authorization", "operation_id": "cycle-rebind", "purpose": "Bind replacement", "increment_id": "INC-0001", "authorization": "DEC-0002", "reason": "Earlier grant superseded", "provenance": {"source": "test user message"}})
        self.mutate({"operation": "prepare-correction", "operation_id": "cycle-correction", "purpose": "Correct failure", "increment_id": "INC-0001", "basis": "technical_failure", "evidence_ids": ["EVD-0001"], "reason": "Fix failed unit check"})
        self.mutate({"operation": "start", "operation_id": "cycle-start", "purpose": "Start correction", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-implemented", "operation_id": "cycle-implemented", "purpose": "Deliver correction", "increment_id": "INC-0001"})
        for check in ("unit", "manual"):
            self.mutate({"operation": "record-evidence", "operation_id": f"cycle-{check}", "purpose": "Verify correction", "evidence": {"increment_id": "INC-0001", "check": check, "result": "passed", "scope": "Corrected greeting"}})
        self.mutate({"operation": "record-review", "operation_id": "cycle-accept", "purpose": "Accept corrected delivery", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "I accept the corrected delivery."}})
        snapshot = self.inspect()
        inc = snapshot["increments"][0]
        self.assertEqual((inc["id"], inc["delivery_revision"], inc["authorization"]), ("INC-0001", 2, "DEC-0002"))
        self.assertEqual((inc["effective_verification"], inc["effective_acceptance"]), ("passed", "accepted"))
        self.assertEqual([ev["delivery_revision"] for ev in snapshot["evidence"]], [1, 2, 2])
        self.assertEqual([review["delivery_revision"] for review in snapshot["reviews"]], [1, 2])
        self.assertTrue(any(event.get("operation") == "rebind-authorization" and any(change["path"] == "increments/INC-0001" and change["before"]["authorization"] == "DEC-0001" and change["after"]["authorization"] == "DEC-0002" for change in event["changes"]) for event in snapshot["history"]))

    def test_documented_defect_reopens_accepted_delivery(self):
        self.delivered()
        self.mutate({"operation": "record-review", "operation_id": "accepted-before-defect", "purpose": "Accept first delivery", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "I accept it."}})
        outcome = self.mutate({"operation": "prepare-correction", "operation_id": "observed-defect", "purpose": "Correct observed defect", "increment_id": "INC-0001", "basis": "documented_defect", "defect": {"description": "Greeting has a defect", "source": "test observation", "criterion": "Returns greeting"}, "reason": "Correct the observed defect"})
        self.assertEqual(outcome["status"], "applied")
        inc = self.inspect()["increments"][0]
        self.assertEqual((inc["delivery_revision"], inc["states"]["acceptance"]), (2, "not_requested"))
