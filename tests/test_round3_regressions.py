from __future__ import annotations

import json
import unittest

from scripts.agile_flow import state_fingerprint
from test_records import RecordsHarness


class RoundThreeRegressions(RecordsHarness, unittest.TestCase):
    def test_t01_project_reopen_rechecks_authorization_of_reactivated_work(self):
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Start", "increment_id": "INC-0001"})
        self.mutate({"operation": "close", "operation_id": "project-close", "purpose": "Close project", "target": "project"})
        self.assertIsNone(self.inspect()["active_increment"])
        self.mutate({"operation": "record-decision", "operation_id": "replacement", "purpose": "Replace authorization", "decision": {"kind": "authorization", "author": "user", "reason": "Continue this work", "scope": {"increment_ids": ["INC-0001"]}, "source": "test user message", "supersedes": ["DEC-0001"]}})
        self.assertEqual(self.mutate({"operation": "reopen", "operation_id": "old-project-reopen", "purpose": "Try reopening under old grant", "target": "project"})["status"], "failed")
        self.mutate({"operation": "rebind-authorization", "operation_id": "rebind", "purpose": "Bind replacement", "increment_id": "INC-0001", "authorization": "DEC-0002", "reason": "Old grant superseded"})
        self.assertEqual(self.mutate({"operation": "reopen", "operation_id": "new-project-reopen", "purpose": "Reopen project with current grant", "target": "project"})["status"], "applied")
        self.assertEqual(self.inspect()["active_increment"], "INC-0001")

    def test_t01_reopen_requires_current_authorization(self):
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Start", "increment_id": "INC-0001"})
        self.mutate({"operation": "close", "operation_id": "close", "purpose": "Close unfinished", "increment_id": "INC-0001"})
        self.mutate({"operation": "record-decision", "operation_id": "replacement", "purpose": "Replace authorization", "decision": {"kind": "authorization", "author": "user", "reason": "Continue this work", "scope": {"increment_ids": ["INC-0001"]}, "source": "test user message", "supersedes": ["DEC-0001"]}})
        self.assertEqual(self.mutate({"operation": "reopen", "operation_id": "old-reopen", "purpose": "Try old grant", "increment_id": "INC-0001"})["status"], "failed")
        self.mutate({"operation": "rebind-authorization", "operation_id": "rebind", "purpose": "Bind replacement", "increment_id": "INC-0001", "authorization": "DEC-0002", "reason": "Old grant superseded"})
        self.assertEqual(self.mutate({"operation": "reopen", "operation_id": "new-reopen", "purpose": "Reopen with current grant", "increment_id": "INC-0001"})["status"], "applied")
        self.assertEqual(self.inspect()["active_increment"], "INC-0001")

    def test_t01_closed_unfinished_work_frees_slot_but_cannot_reopen_into_conflict(self):
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

    def test_t02_nonbehavioral_change_needs_current_checks_and_new_acceptance(self):
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Start", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-implemented", "operation_id": "implemented", "purpose": "Deliver", "increment_id": "INC-0001"})
        covered = self.root / "app.py"
        covered.write_text("first\n")
        for check in ("unit", "manual"):
            self.mutate({"operation": "record-evidence", "operation_id": f"initial-{check}", "purpose": "Initial check", "evidence": {"increment_id": "INC-0001", "check": check, "result": "passed", "scope": "app.py", "paths": ["app.py"]}})
        self.mutate({"operation": "record-review", "operation_id": "initial-review", "purpose": "Review first state", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "I accept the first state."}})
        covered.write_text("second\n")
        self.assertEqual((self.inspect()["increments"][0]["effective_verification"], self.inspect()["increments"][0]["effective_acceptance"]), ("not_run", "pending"))
        refused = self.mutate({"operation": "record-evidence", "operation_id": "unclassified-rerun", "purpose": "Try unclassified rerun", "evidence": {"increment_id": "INC-0001", "check": "unit", "result": "passed", "scope": "app.py", "paths": ["app.py"]}})
        self.assertEqual(refused["status"], "failed")
        for check in ("unit", "manual"):
            self.mutate({"operation": "record-evidence", "operation_id": f"fresh-{check}", "purpose": "Reassess non-behavioral change", "evidence": {"increment_id": "INC-0001", "check": check, "result": "passed", "scope": "app.py", "paths": ["app.py"], "change_impact": "non_behavioral", "impact_reason": "Only formatting changed"}})
        inc = self.inspect()["increments"][0]
        self.assertEqual((inc["effective_verification"], inc["effective_acceptance"]), ("passed", "pending"))
        self.mutate({"operation": "record-review", "operation_id": "fresh-review", "purpose": "Accept reassessed state", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "I accept the reassessed state."}})
        snapshot = self.inspect()
        self.assertEqual((snapshot["increments"][0]["effective_verification"], snapshot["increments"][0]["effective_acceptance"]), ("passed", "accepted"))
        self.assertEqual(len(snapshot["evidence"]), 4)
        self.assertEqual(snapshot["reviews"][-1]["evidence_ids"], ["EVD-0003", "EVD-0004"])
        view = (self.root / ".agile-flow" / "views" / "increments" / "INC-0001.md").read_text()
        self.assertIn("Current verification: passed", view)
        self.assertIn("Current acceptance: accepted", view)

    def test_t02_behavior_change_requires_new_revision_and_review(self):
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Start", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-implemented", "operation_id": "implemented", "purpose": "Deliver", "increment_id": "INC-0001"})
        covered = self.root / "app.py"
        covered.write_text("first\n")
        for check in ("unit", "manual"):
            self.mutate({"operation": "record-evidence", "operation_id": f"old-{check}", "purpose": "Check first delivery", "evidence": {"increment_id": "INC-0001", "check": check, "result": "passed", "scope": "app.py", "paths": ["app.py"]}})
        self.mutate({"operation": "record-review", "operation_id": "old-accept", "purpose": "Accept first delivery", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "I accept delivery one."}})
        covered.write_text("behavior changed\n")
        refused = self.mutate({"operation": "record-evidence", "operation_id": "invalid-same-revision", "purpose": "Attempt to reuse revision", "evidence": {"increment_id": "INC-0001", "check": "unit", "result": "passed", "scope": "app.py", "paths": ["app.py"], "change_impact": "behavior_affecting", "impact_reason": "Greeting behavior changed"}})
        self.assertEqual(refused["status"], "failed")
        self.mutate({"operation": "mark-delivery-change", "operation_id": "behavior-change", "purpose": "Record behavior change", "increment_id": "INC-0001", "reason": "Greeting behavior changed"})
        self.assertEqual((self.inspect()["increments"][0]["delivery_revision"], self.inspect()["increments"][0]["effective_acceptance"]), (2, "pending"))
        for check in ("unit", "manual"):
            self.mutate({"operation": "record-evidence", "operation_id": f"new-{check}", "purpose": "Check new delivery", "evidence": {"increment_id": "INC-0001", "check": check, "result": "passed", "scope": "app.py", "paths": ["app.py"]}})
        inc = self.inspect()["increments"][0]
        self.assertEqual((inc["effective_verification"], inc["effective_acceptance"]), ("passed", "pending"))
        self.mutate({"operation": "record-review", "operation_id": "new-accept", "purpose": "Accept second delivery", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "I accept delivery two."}})
        self.assertEqual(self.inspect()["increments"][0]["effective_acceptance"], "accepted")

    def test_t02_new_check_does_not_inherit_earlier_acceptance(self):
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Start", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-implemented", "operation_id": "implemented", "purpose": "Deliver", "increment_id": "INC-0001"})
        self.mutate({"operation": "record-evidence", "operation_id": "first-unit", "purpose": "Initial unit check", "evidence": {"increment_id": "INC-0001", "check": "unit", "result": "passed", "scope": "Greeting"}})
        self.mutate({"operation": "record-review", "operation_id": "early-accept", "purpose": "Accept with manual check outstanding", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "I accept it with the manual check outstanding."}})
        self.assertEqual(self.inspect()["increments"][0]["effective_acceptance"], "accepted")
        self.mutate({"operation": "record-evidence", "operation_id": "later-manual", "purpose": "Later manual check", "evidence": {"increment_id": "INC-0001", "check": "manual", "result": "passed", "scope": "Greeting"}})
        self.assertEqual((self.inspect()["increments"][0]["effective_verification"], self.inspect()["increments"][0]["effective_acceptance"]), ("passed", "pending"))

    def test_t02_legacy_review_without_binding_remains_readable_and_conservative(self):
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
        self.assertEqual(self.inspect()["increments"][0]["effective_acceptance"], "pending")
        covered.write_text("second\n")
        self.assertEqual(self.inspect()["increments"][0]["effective_acceptance"], "pending")

    def test_t02_legacy_review_without_reconstructible_history_is_pending(self):
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
