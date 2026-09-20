from __future__ import annotations

import unittest

from test_records import RecordsHarness


class ReauditRegressions(RecordsHarness, unittest.TestCase):
    def delivered(self, criteria=None):
        if criteria is None:
            self.prepared()
        else:
            self.initialize(); self.backlog(); self.authorization()
            self.mutate({"operation": "prepare", "operation_id": "prepare-parts", "purpose": "Prepare parts", "increment": {"item_ids": ["ITEM-0001"], "objective": "Deliver parts", "scope": "Response", "criteria": criteria, "required_checks": ["unit"], "authorization": "DEC-0001"}})
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Start", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-implemented", "operation_id": "implemented", "purpose": "Deliver", "increment_id": "INC-0001"})

    def test_r01_view_matches_effective_state_after_external_edit(self):
        self.delivered()
        product_file = self.root / "app.py"
        product_file.write_text("first\n")
        for check in ("unit", "manual"):
            self.mutate({"operation": "record-evidence", "operation_id": f"check-{check}", "purpose": "Verify", "evidence": {"increment_id": "INC-0001", "check": check, "result": "passed", "scope": "app.py", "paths": ["app.py"]}})
        self.mutate({"operation": "record-review", "operation_id": "accept", "purpose": "Accept", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "I accept this delivery."}})
        product_file.write_text("second\n")
        state = self.inspect()["increments"][0]
        self.assertEqual((state["effective_verification"], state["effective_acceptance"]), ("not_run", "pending"))
        self.call("render")
        view = (self.root / ".agile-flow" / "views" / "increments" / "INC-0001.md").read_text()
        self.assertIn("Current verification: not_run", view)
        self.assertIn("Current acceptance: pending", view)
        self.assertIn("Stale evidence", view)
        summary = (self.root / ".agile-flow" / "views" / "summary.md").read_text()
        self.assertIn("not_run", summary)
        self.assertIn("pending", summary)
        self.assertEqual(self.inspect()["increments"][0]["effective_acceptance"], "pending")

    def test_r02_failed_check_reopens_same_increment_without_user_review(self):
        self.delivered()
        self.mutate({"operation": "record-evidence", "operation_id": "failed", "purpose": "Observed failure", "evidence": {"increment_id": "INC-0001", "check": "unit", "result": "failed", "scope": "Greeting endpoint"}})
        outcome = self.mutate({"operation": "prepare-correction", "operation_id": "technical-correction", "purpose": "Fix failed check", "increment_id": "INC-0001", "basis": "technical_failure", "evidence_ids": ["EVD-0001"], "reason": "Unit check failed."})
        self.assertEqual(outcome["status"], "applied")
        inc = self.inspect()["increments"][0]
        self.assertEqual((inc["id"], inc["delivery_revision"], inc["states"]["development"]), ("INC-0001", 2, "ready"))
        self.assertEqual(self.inspect()["reviews"], [])

    def test_r03_explicit_review_supersession_is_scoped(self):
        self.delivered(["Greeting", "Label"])
        self.mutate({"operation": "record-review", "operation_id": "changes", "purpose": "Request changes", "review": {"increment_id": "INC-0001", "decision": "changes_requested", "parts": ["Greeting", "Label"], "requested_changes": ["Adjust both parts"], "user_quote": "Adjust both parts."}})
        self.mutate({"operation": "record-review", "operation_id": "accept-greeting", "purpose": "Accept greeting", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Greeting"], "supersedes": [{"review_id": "REV-0001", "parts": ["Greeting"]}], "user_quote": "I withdraw the greeting change and accept it."}})
        self.assertEqual(self.inspect()["increments"][0]["states"]["acceptance"], "changes_requested")
        self.mutate({"operation": "record-review", "operation_id": "accept-label", "purpose": "Accept label", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Label"], "supersedes": [{"review_id": "REV-0001", "parts": ["Label"]}], "user_quote": "I withdraw the label change and accept it."}})
        self.assertEqual(self.inspect()["increments"][0]["states"]["acceptance"], "accepted")
        self.assertEqual(len(self.inspect()["reviews"]), 3)

    def test_r04_replacement_authorization_resumes_and_corrects_same_increment(self):
        self.delivered()
        self.mutate({"operation": "record-review", "operation_id": "changes", "purpose": "Request correction", "review": {"increment_id": "INC-0001", "decision": "changes_requested", "user_quote": "Correct the greeting."}})
        self.mutate({"operation": "record-decision", "operation_id": "replacement", "purpose": "Replace grant", "decision": {"kind": "authorization", "author": "user", "reason": "Continue this increment", "scope": {"increment_ids": ["INC-0001"]}, "source": "new user message", "supersedes": ["DEC-0001"]}})
        self.assertEqual(self.mutate({"operation": "prepare-correction", "operation_id": "old-grant", "purpose": "Attempt correction", "increment_id": "INC-0001", "reason": "Correct greeting."})["status"], "failed")
        outcome = self.mutate({"operation": "rebind-authorization", "operation_id": "rebind", "purpose": "Use replacement grant", "reason": "The user superseded the earlier authorization.", "increment_id": "INC-0001", "authorization": "DEC-0002", "provenance": {"source": "new user message"}})
        self.assertEqual(outcome["status"], "applied")
        self.assertEqual(self.inspect()["increments"][0]["authorization"], "DEC-0002")
        self.assertEqual(self.mutate({"operation": "prepare-correction", "operation_id": "new-grant", "purpose": "Correct", "increment_id": "INC-0001", "reason": "Correct greeting."})["status"], "applied")

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

    def test_withdrawal_restores_prior_acceptance_without_erasing_reviews(self):
        self.delivered()
        self.mutate({"operation": "record-review", "operation_id": "first-accept", "purpose": "Accept", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "Accepted."}})
        self.mutate({"operation": "record-review", "operation_id": "later-change", "purpose": "Request change", "review": {"increment_id": "INC-0001", "decision": "changes_requested", "parts": ["Returns greeting"], "user_quote": "Change it."}})
        self.assertEqual(self.inspect()["increments"][0]["states"]["acceptance"], "changes_requested")
        self.mutate({"operation": "record-review", "operation_id": "withdraw-change", "purpose": "Withdraw request", "review": {"increment_id": "INC-0001", "decision": "withdrawn", "supersedes": [{"review_id": "REV-0002", "parts": ["Returns greeting"]}], "user_quote": "I withdraw the change request."}})
        self.assertEqual(self.inspect()["increments"][0]["states"]["acceptance"], "accepted")
        self.assertEqual(len(self.inspect()["reviews"]), 3)

    def test_invalid_replacement_authorization_does_not_rebind(self):
        self.delivered()
        self.mutate({"operation": "record-decision", "operation_id": "unrelated-grant", "purpose": "Record unrelated grant", "decision": {"kind": "authorization", "author": "user", "reason": "Other work", "scope": {"increment_ids": ["INC-OTHER"]}, "source": "test user message"}})
        result = self.mutate({"operation": "rebind-authorization", "operation_id": "reject-unrelated", "purpose": "Try unrelated grant", "increment_id": "INC-0001", "authorization": "DEC-0002", "reason": "Try replacement"})
        self.assertEqual(result["status"], "failed")
        self.assertEqual(self.inspect()["increments"][0]["authorization"], "DEC-0001")

    def test_superseded_grant_can_be_replaced_before_resume(self):
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "resume-start", "purpose": "Start work", "increment_id": "INC-0001"})
        self.mutate({"operation": "pause", "operation_id": "resume-pause", "purpose": "Pause work", "increment_id": "INC-0001"})
        self.mutate({"operation": "record-decision", "operation_id": "resume-grant", "purpose": "Replace grant", "decision": {"kind": "authorization", "author": "user", "reason": "Resume this increment", "scope": {"increment_ids": ["INC-0001"]}, "source": "test user message", "supersedes": ["DEC-0001"]}})
        self.assertEqual(self.mutate({"operation": "resume", "operation_id": "resume-old", "purpose": "Attempt old grant", "increment_id": "INC-0001"})["status"], "failed")
        self.mutate({"operation": "rebind-authorization", "operation_id": "resume-rebind", "purpose": "Bind new grant", "increment_id": "INC-0001", "authorization": "DEC-0002", "reason": "Old grant superseded", "provenance": {"source": "test user message"}})
        self.assertEqual(self.mutate({"operation": "resume", "operation_id": "resume-new", "purpose": "Resume work", "increment_id": "INC-0001"})["status"], "applied")
        inc = self.inspect()["increments"][0]
        self.assertEqual((inc["authorization"], inc["delivery_revision"], inc["suspended"]), ("DEC-0002", 1, False))
