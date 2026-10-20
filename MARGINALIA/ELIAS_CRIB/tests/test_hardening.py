"""FICTIONAL / NON-EVIDENTIARY: hardening tests."""
import importlib.util
import multiprocessing
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("platinum", Path(__file__).resolve().parents[1] / "platinum.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

def worker(path, index):
    p.append(path, "worker " + str(index))

class HardeningTests(unittest.TestCase):
    def test_concurrent_writers_and_external_anchor(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            work = root / "work"
            work.mkdir()
            (work / "events.jsonl").write_bytes(b"")
            jobs = [multiprocessing.Process(target=worker, args=(work, i)) for i in range(12)]
            for job in jobs:
                job.start()
            for job in jobs:
                job.join(10)
                self.assertEqual(job.exitcode, 0)
            self.assertEqual(p.verify_bytes((work / "events.jsonl").read_bytes())["sequence"], 12)
            marker = root / "anchor.json"
            self.assertEqual(p.anchor(work, marker)["sequence"], 12)
            self.assertEqual(p.check_anchor(work, marker)["sequence"], 12)
            p.append(work, "new entry")
            with self.assertRaises(ValueError):
                p.check_anchor(work, marker)

    def test_bounds_and_deterministic_reflection(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "events.jsonl").write_bytes(b"")
            p.append(root, "first")
            with self.assertRaises(ValueError):
                p.append(root, "x" * 5000)
            with self.assertRaises(ValueError):
                p.verify_bytes((root / "events.jsonl").read_bytes()[:-2])
            response = p.reflect("What evidence?", {"source": "AUTHORITY.json", "sha256": "a" * 64})
            self.assertEqual(response["automated_actions"], 0)

if __name__ == "__main__":
    unittest.main()
