"""End-to-end Crib exercise. FICTIONAL / NON-EVIDENTIARY."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location("audit_" + name, BASE / (name + ".py"))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

crib = load("crib")
doorway = load("doorway")
recovery = load("recovery")
platinum = load("platinum")

class IntegrationAudit(unittest.TestCase):
    def test_source_record_checkpoint_restore(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            garden = root / "garden"
            garden.mkdir()
            source = garden / "apple.md"
            source.write_bytes((BASE / "EASTER_EGG.md").read_bytes())
            source_before = source.read_bytes()
            opened = doorway.read_source(garden, "apple.md", hashlib.sha256(source_before).hexdigest())
            self.assertIn("APPLE", opened["content"])
            crib.init(root / "work")
            crib.record(root / "work", "Source reviewed: " + opened["sha256"])
            platinum.append(root / "work", "Alternative interpretations remain possible", kind="revision")
            manifest = recovery.snapshot(root / "work", root / "backup")
            self.assertEqual(recovery.check_snapshot(root / "backup"), manifest)
            self.assertEqual(recovery.restore(root / "backup", root / "restored"), manifest)
            self.assertEqual(crib.verify(root / "restored")[0], 2)
            self.assertEqual(source.read_bytes(), source_before)
            self.assertEqual(platinum.reflect("What can we infer?", opened)["automated_actions"], 0)

    def test_original_writer_is_locked_writer(self):
        with tempfile.TemporaryDirectory() as temp:
            crib.init(temp + "/work")
            crib.record(temp + "/work", "one")
            platinum.append(temp + "/work", "two")
            self.assertEqual(crib.verify(temp + "/work")[0], 2)

if __name__ == "__main__":
    unittest.main()
