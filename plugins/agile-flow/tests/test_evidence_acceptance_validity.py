"""Evidence acceptance validity behavior of the shared lifecycle engine."""
import unittest

from record_scenarios import DeliveredRecordsHarness


class EvidenceAcceptanceValidityTests(DeliveredRecordsHarness, unittest.TestCase):
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

    def test_view_matches_effective_state_after_external_edit(self):
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

    def test_nonbehavioral_change_needs_current_checks_and_new_acceptance(self):
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

    def test_behavior_change_requires_new_revision_and_review(self):
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

    def test_new_check_preserves_unchanged_delivery_acceptance(self):
        self.prepared()
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Start", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-implemented", "operation_id": "implemented", "purpose": "Deliver", "increment_id": "INC-0001"})
        self.mutate({"operation": "record-evidence", "operation_id": "first-unit", "purpose": "Initial unit check", "evidence": {"increment_id": "INC-0001", "check": "unit", "result": "passed", "scope": "Greeting"}})
        self.mutate({"operation": "record-review", "operation_id": "early-accept", "purpose": "Accept with manual check outstanding", "review": {"increment_id": "INC-0001", "decision": "accepted", "parts": ["Returns greeting"], "user_quote": "I accept it with the manual check outstanding."}})
        self.assertEqual(self.inspect()["increments"][0]["effective_acceptance"], "accepted")
        self.mutate({"operation": "record-evidence", "operation_id": "later-manual", "purpose": "Later manual check", "evidence": {"increment_id": "INC-0001", "check": "manual", "result": "passed", "scope": "Greeting"}})
        self.assertEqual((self.inspect()["increments"][0]["effective_verification"], self.inspect()["increments"][0]["effective_acceptance"]), ("passed", "accepted"))

    def test_repeated_checks_preserve_acceptance_but_changed_files_do_not(self):
        self.prepared()
        for operation in ('start', 'mark-implemented'):
            self.mutate(dict(operation=operation, operation_id=operation, purpose=operation, increment_id='INC-0001'))
        covered = self.root / 'app.py'
        covered.write_text('print("Hello")\n')

        def check(name, attempt, **extra):
            result = self.mutate(dict(operation='record-evidence', operation_id=attempt, purpose=attempt,
                evidence=dict(increment_id='INC-0001', check=name, result='passed', scope='Greeting', paths=['app.py'], **extra)))
            self.assertEqual(result['status'], 'applied')

        check('unit', 'unit-first')
        self.mutate(dict(operation='record-review', operation_id='accept', purpose='Accept with manual check outstanding',
            review=dict(increment_id='INC-0001', decision='accepted', parts=['Returns greeting'], user_quote='I accept the delivery with manual verification outstanding.')))
        for name, attempt in [('manual', 'manual-first'), ('unit', 'unit-rerun')]:
            check(name, attempt)
            inc = self.inspect()['increments'][0]
            self.assertEqual((inc['delivery_revision'], inc['effective_verification'], inc['effective_acceptance']), (1, 'passed', 'accepted'))
            self.assertIn('Current acceptance: accepted', (self.root / '.agile-flow/views/increments/INC-0001.md').read_text())
        covered.write_text('print("Hello")  # formatting comment\n')
        for name in ('unit', 'manual'):
            check(name, name + '-changed', change_impact='non_behavioral', impact_reason='Comment only')
        inc = self.inspect()['increments'][0]
        self.assertEqual((inc['effective_verification'], inc['effective_acceptance']), ('passed', 'pending'))
        self.assertEqual(len(self.inspect()['reviews']), 1)
