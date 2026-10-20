"""FICTIONAL / NON-EVIDENTIARY: integrity tests for a local prototype."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "crib.py"
spec = importlib.util.spec_from_file_location("crib", MODULE)
crib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crib)

class CribTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            crib.init(folder)
            crib.record(folder, "First observation")
            crib.record(folder, "Second observation")
            self.assertEqual(crib.verify(folder)[0], 2)

    def test_tamper_detection(self):
        with tempfile.TemporaryDirectory() as folder:
            crib.init(folder)
            crib.record(folder, "Original")
            log = Path(folder) / "events.jsonl"
            events = [json.loads(line) for line in log.read_text().splitlines()]
            events[0]["statement"] = "Changed"
            log.write_text(json.dumps(events[0]) + "\n")
            with self.assertRaises(ValueError):
                crib.verify(folder)

    def test_reject_nonempty_workspace(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "existing").write_text("keep")
            with self.assertRaises(ValueError):
                crib.init(folder)

if __name__ == "__main__":
    unittest.main()
