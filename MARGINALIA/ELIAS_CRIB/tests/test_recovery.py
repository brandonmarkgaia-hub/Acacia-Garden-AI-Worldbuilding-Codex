"""FICTIONAL / NON-EVIDENTIARY: snapshot and recovery tests."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
def load(name):
    spec = importlib.util.spec_from_file_location(name, root / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
crib = load("crib")
recovery = load("recovery")

class RecoveryTests(unittest.TestCase):
    def test_snapshot_and_restore(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            workspace, backup, restored = (base / n for n in ("work", "backup", "restored"))
            crib.init(workspace)
            crib.record(workspace, "first")
            crib.record(workspace, "second")
            original = recovery.snapshot(workspace, backup)
            self.assertEqual(recovery.check_snapshot(backup), original)
            self.assertEqual(recovery.restore(backup, restored), original)
            self.assertEqual(crib.verify(restored)[0], 2)

    def test_snapshot_detects_truncation(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            work, backup = base / "work", base / "backup"
            crib.init(work)
            crib.record(work, "first")
            crib.record(work, "second")
            recovery.snapshot(work, backup)
            lines = (backup / "events.jsonl").read_text().splitlines()
            (backup / "events.jsonl").write_text(lines[0] + "\n")
            with self.assertRaises(ValueError):
                recovery.check_snapshot(backup)

    def test_reject_existing_restore_target(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            crib.init(base / "work")
            recovery.snapshot(base / "work", base / "backup")
            (base / "target").mkdir()
            with self.assertRaises(ValueError):
                recovery.restore(base / "backup", base / "target")

    def test_reject_incomplete_event(self):
        with tempfile.TemporaryDirectory() as folder:
            crib.init(folder)
            (Path(folder) / "events.jsonl").write_text('{"incomplete":true}')
            with self.assertRaises(ValueError):
                recovery.inspect_journal(folder)

if __name__ == "__main__":
    unittest.main()
