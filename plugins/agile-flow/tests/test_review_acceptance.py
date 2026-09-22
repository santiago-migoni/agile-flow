"""Review acceptance behavior of the shared lifecycle engine."""
import unittest

from record_scenarios import DeliveredRecordsHarness


class ReviewAcceptanceTests(DeliveredRecordsHarness, unittest.TestCase):
    def test_stale_review_cannot_accept_current_delivery_and_partial_parts_accumulate(self):
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

    def test_explicit_review_supersession_is_scoped(self):
        self.delivered(["Greeting", "Label"])
        self.mutate({"operation": "record-review", "operation_id": "changes", "purpose": "Request changes", "review": {"increment_id": "INC-0001", "decision": "changes_requested", "parts": ["Greeting", "Label"], "requested_changes": ["Adjust both parts"], "user_quote": "Adjust both parts."}})
        self.mutate({"operation": "record-review", "operation_id": "accept-greeting", "purpose": "Accept greeting", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Greeting"], "supersedes": [{"review_id": "REV-0001", "parts": ["Greeting"]}], "user_quote": "I withdraw the greeting change and accept it."}})
        self.assertEqual(self.inspect()["increments"][0]["states"]["acceptance"], "changes_requested")
        self.mutate({"operation": "record-review", "operation_id": "accept-label", "purpose": "Accept label", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Label"], "supersedes": [{"review_id": "REV-0001", "parts": ["Label"]}], "user_quote": "I withdraw the label change and accept it."}})
        self.assertEqual(self.inspect()["increments"][0]["states"]["acceptance"], "accepted")
        self.assertEqual(len(self.inspect()["reviews"]), 3)

    def test_withdrawal_restores_prior_acceptance_without_erasing_reviews(self):
        self.delivered()
        self.mutate({"operation": "record-review", "operation_id": "first-accept", "purpose": "Accept", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "Accepted."}})
        self.mutate({"operation": "record-review", "operation_id": "later-change", "purpose": "Request change", "review": {"increment_id": "INC-0001", "decision": "changes_requested", "parts": ["Returns greeting"], "user_quote": "Change it."}})
        self.assertEqual(self.inspect()["increments"][0]["states"]["acceptance"], "changes_requested")
        self.mutate({"operation": "record-review", "operation_id": "withdraw-change", "purpose": "Withdraw request", "review": {"increment_id": "INC-0001", "decision": "withdrawn", "supersedes": [{"review_id": "REV-0002", "parts": ["Returns greeting"]}], "user_quote": "I withdraw the change request."}})
        self.assertEqual(self.inspect()["increments"][0]["states"]["acceptance"], "accepted")
        self.assertEqual(len(self.inspect()["reviews"]), 3)
