"""Authorization behavior of the shared lifecycle engine."""
import unittest

from record_scenarios import DeliveredRecordsHarness


class AuthorizationTests(DeliveredRecordsHarness, unittest.TestCase):
    def test_technical_and_superseded_decisions_do_not_authorize(self):
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

    def test_replacement_authorization_resumes_and_corrects_same_increment(self):
        self.delivered()
        self.mutate({"operation": "record-review", "operation_id": "changes", "purpose": "Request correction", "review": {"increment_id": "INC-0001", "decision": "changes_requested", "user_quote": "Correct the greeting."}})
        self.mutate({"operation": "record-decision", "operation_id": "replacement", "purpose": "Replace grant", "decision": {"kind": "authorization", "author": "user", "reason": "Continue this increment", "scope": {"increment_ids": ["INC-0001"]}, "source": "new user message", "supersedes": ["DEC-0001"]}})
        self.assertEqual(self.mutate({"operation": "prepare-correction", "operation_id": "old-grant", "purpose": "Attempt correction", "increment_id": "INC-0001", "reason": "Correct greeting."})["status"], "failed")
        outcome = self.mutate({"operation": "rebind-authorization", "operation_id": "rebind", "purpose": "Use replacement grant", "reason": "The user superseded the earlier authorization.", "increment_id": "INC-0001", "authorization": "DEC-0002", "provenance": {"source": "new user message"}})
        self.assertEqual(outcome["status"], "applied")
        self.assertEqual(self.inspect()["increments"][0]["authorization"], "DEC-0002")
        self.assertEqual(self.mutate({"operation": "prepare-correction", "operation_id": "new-grant", "purpose": "Correct", "increment_id": "INC-0001", "reason": "Correct greeting."})["status"], "applied")

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

    def test_project_reopen_rechecks_authorization_of_reactivated_work(self):
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Start", "increment_id": "INC-0001"})
        self.mutate({"operation": "close", "operation_id": "project-close", "purpose": "Close project", "target": "project"})
        self.assertIsNone(self.inspect()["active_increment"])
        self.mutate({"operation": "record-decision", "operation_id": "replacement", "purpose": "Replace authorization", "decision": {"kind": "authorization", "author": "user", "reason": "Continue this work", "scope": {"increment_ids": ["INC-0001"]}, "source": "test user message", "supersedes": ["DEC-0001"]}})
        self.assertEqual(self.mutate({"operation": "reopen", "operation_id": "old-project-reopen", "purpose": "Try reopening under old grant", "target": "project"})["status"], "failed")
        self.mutate({"operation": "rebind-authorization", "operation_id": "rebind", "purpose": "Bind replacement", "increment_id": "INC-0001", "authorization": "DEC-0002", "reason": "Old grant superseded"})
        self.assertEqual(self.mutate({"operation": "reopen", "operation_id": "new-project-reopen", "purpose": "Reopen project with current grant", "target": "project"})["status"], "applied")
        self.assertEqual(self.inspect()["active_increment"], "INC-0001")

    def test_reopen_requires_current_authorization(self):
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Start", "increment_id": "INC-0001"})
        self.mutate({"operation": "close", "operation_id": "close", "purpose": "Close unfinished", "increment_id": "INC-0001"})
        self.mutate({"operation": "record-decision", "operation_id": "replacement", "purpose": "Replace authorization", "decision": {"kind": "authorization", "author": "user", "reason": "Continue this work", "scope": {"increment_ids": ["INC-0001"]}, "source": "test user message", "supersedes": ["DEC-0001"]}})
        self.assertEqual(self.mutate({"operation": "reopen", "operation_id": "old-reopen", "purpose": "Try old grant", "increment_id": "INC-0001"})["status"], "failed")
        self.mutate({"operation": "rebind-authorization", "operation_id": "rebind", "purpose": "Bind replacement", "increment_id": "INC-0001", "authorization": "DEC-0002", "reason": "Old grant superseded"})
        self.assertEqual(self.mutate({"operation": "reopen", "operation_id": "new-reopen", "purpose": "Reopen with current grant", "increment_id": "INC-0001"})["status"], "applied")
        self.assertEqual(self.inspect()["active_increment"], "INC-0001")
