"""Record history behavior of the shared lifecycle engine."""
import unittest

from record_scenarios import DeliveredRecordsHarness


class RecordHistoryTests(DeliveredRecordsHarness, unittest.TestCase):
    def test_history_keeps_multiple_prior_values_and_provenance(self):
        self.initialize(); self.backlog()
        for number, purpose in enumerate(("Revised need", "Final need"), 1):
            self.mutate({"operation": "update-backlog", "operation_id": f"update-{number}", "purpose": f"Revision {number}", "provenance": {"source": "user message"}, "item": {"id": "ITEM-0001", "purpose": purpose}})
        changes = [entry for entry in self.inspect()["history"] if entry["operation"] == "update-backlog"]
        self.assertEqual([entry["changes"][0]["before"]["purpose"] for entry in changes[1:]], ["Show a greeting.", "Revised need"])
        self.assertEqual(changes[-1]["provenance"]["source"], "user message")

    def test_replay_metadata_matches_committed_state(self):
        initialized = self.initialize()
        request = {"operation": "initialize", "operation_id": "op-init", "purpose": "Create a test project.", "project": {"name": "Test", "purpose": "Verify records."}}
        _, replay = self.call("mutate", request)
        self.assertEqual((replay["revision"], replay["fingerprint"]), (initialized["revision"], initialized["fingerprint"]))
        applied = self.mutate({"operation": "record-decision", "operation_id": "decision", "purpose": "Technical choice", "decision": {"kind": "technical", "author": "agent", "reason": "Simple", "scope": "Project", "source": "local analysis"}})
        _, replay = self.call("mutate", {"operation": "record-decision", "operation_id": "decision", "purpose": "Technical choice", "decision": {"kind": "technical", "author": "agent", "reason": "Simple", "scope": "Project", "source": "local analysis"}})
        self.assertEqual((applied["revision"], applied["fingerprint"]), (replay["revision"], replay["fingerprint"]))
