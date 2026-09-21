import unittest
from test_records import RecordsHarness
import importlib.util
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts" / "legacy_records.py"
SPEC = importlib.util.spec_from_file_location("agile_flow_records", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RecoveryTest(RecordsHarness, unittest.TestCase):
    def test_backup_and_recovery_are_explicit(self) -> None:
        self.initialize(); self.backlog()
        state = self.root / ".agile-flow" / "state.json"; state.write_text("{broken", encoding="utf-8")
        code, body = self.call("recover")
        self.assertEqual((code, body["status"]), (0, "applied"))
        self.assertEqual(len(list((self.root / ".agile-flow").glob("state.damaged.*.json"))), 1)
        self.assertEqual(self.inspect()["project"]["name"], "Test")

    def test_no_git_project_remains_valid(self) -> None:
        self.initialize(); code, body = self.call("validate")
        self.assertEqual((code, body["status"]), (0, "ok"))

    def test_interrupted_recovery_keeps_canonical_and_backup(self) -> None:
        self.initialize(); self.backlog()
        store = MODULE.Store(self.root)
        before = store.path.read_bytes()
        backup = store.backup.read_bytes()
        with patch.object(MODULE.os, "replace", side_effect=OSError("simulated replace failure")):
            with self.assertRaises(OSError):
                store.recover()
        self.assertEqual(store.path.read_bytes(), before)
        self.assertEqual(store.backup.read_bytes(), backup)
        self.assertEqual(len(list(store.directory.glob("state.damaged.*.json"))), 1)

    def test_repeated_recovery_preserves_distinct_damaged_snapshots(self) -> None:
        self.initialize(); self.backlog()
        state = self.root / ".agile-flow" / "state.json"
        state.write_text("{first", encoding="utf-8")
        self.call("recover")
        state.write_text("{second", encoding="utf-8")
        self.call("recover")
        snapshots = list((self.root / ".agile-flow").glob("state.damaged.*.json"))
        self.assertEqual(len(snapshots), 2)
        self.assertEqual({path.read_text() for path in snapshots}, {"{first", "{second"})

    def test_saved_state_is_reported_when_view_generation_fails(self) -> None:
        store = MODULE.Store(self.root)
        request = {"operation": "initialize", "operation_id": "init-view-failure", "purpose": "Create fixture", "project": {"name": "Fixture", "purpose": "Check committed state."}}
        with patch.object(MODULE, "render", side_effect=OSError("simulated view failure")):
            result = store.transaction(request)
        self.assertEqual((result["status"], result["views"]), ("applied", "failed"))
        self.assertEqual(store.read()["project"]["name"], "Fixture")
