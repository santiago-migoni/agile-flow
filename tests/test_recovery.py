import unittest
from test_records import RecordsHarness


class RecoveryTest(RecordsHarness, unittest.TestCase):
    def test_backup_and_recovery_are_explicit(self) -> None:
        self.initialize(); self.backlog()
        state = self.root / ".agile-flow" / "state.json"; state.write_text("{broken", encoding="utf-8")
        code, body = self.call("recover")
        self.assertEqual((code, body["status"]), (0, "applied"))
        self.assertTrue((self.root / ".agile-flow" / "state.corrupt.json").exists())
        self.assertEqual(self.inspect()["project"]["name"], "Test")

    def test_no_git_project_remains_valid(self) -> None:
        self.initialize(); code, body = self.call("validate")
        self.assertEqual((code, body["status"]), (0, "ok"))
