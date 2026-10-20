"""FICTIONAL / NON-EVIDENTIARY: read-only doorway tests."""
import importlib.util
import hashlib
import tempfile
import unittest
from pathlib import Path

module_path = Path(__file__).resolve().parents[1] / "doorway.py"
spec = importlib.util.spec_from_file_location("doorway", module_path)
doorway = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doorway)

class DoorwayTests(unittest.TestCase):
    def test_read_and_hash(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "sample.md").write_text("Garden", encoding="utf-8")
            expected = hashlib.sha256(b"Garden").hexdigest()
            result = doorway.read_source(root, "sample.md", expected)
            self.assertEqual(result["sha256"], expected)
            self.assertEqual(result["content"], "Garden")
            self.assertEqual((root / "sample.md").read_text(), "Garden")

    def test_reject_parent_traversal(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                doorway.read_source(folder, "../outside.md")

    def test_reject_changed_source(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "sample.md").write_text("changed")
            with self.assertRaises(ValueError):
                doorway.read_source(folder, "sample.md", "0" * 64)

    def test_reject_symlink_escape(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as outside:
            (Path(outside) / "secret.md").write_text("secret")
            (Path(folder) / "link.md").symlink_to(Path(outside) / "secret.md")
            with self.assertRaises(ValueError):
                doorway.read_source(folder, "link.md")

if __name__ == "__main__":
    unittest.main()
