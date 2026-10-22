import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from retrieval_envelope import emit, digest, verify_record

class EnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "safe.md").write_text("Keeper note. Witness dissent.\n", encoding="utf-8")
        self.manifest = {"status": "advisory_not_canon", "documents": [{"path": "safe.md"}]}

    def test_exact_integrity(self):
        original = (self.root / "safe.md").read_text()
        record = next(emit(self.root, self.manifest, size=10))
        self.assertTrue(verify_record(record, original, digest(original)))
        self.assertFalse(verify_record({**record, "text": "altered"}, original, digest(original)))
        self.assertFalse(verify_record(record, original, "0" * 64))

    def test_unknown_classification_and_read_only(self):
        original = (self.root / "safe.md").read_bytes()
        records = list(emit(self.root, self.manifest))
        self.assertEqual(records[0]["voice_class"], "unknown_pending_provenance_resolution")
        self.assertEqual((self.root / "safe.md").read_bytes(), original)

    def test_pinned_hash_rejects_tampering(self):
        self.manifest["documents"][0]["expected_source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            list(emit(self.root, self.manifest))

    def test_path_traversal_rejected(self):
        self.manifest["documents"][0]["path"] = "../escape.md"
        with self.assertRaisesRegex(ValueError, "unsafe"):
            list(emit(self.root, self.manifest))

    def test_duplicate_manifest_paths_rejected(self):
        self.manifest["documents"].append({"path": "safe.md"})
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            list(emit(self.root, self.manifest))

    def test_mixed_voice_is_not_collapsed(self):
        self.manifest["documents"][0]["voice_class"] = "mixed_keeper_testimony_and_witness_dissent"
        rows = list(emit(self.root, self.manifest, size=8))
        self.assertTrue(all(r["voice_class"].startswith("mixed_") for r in rows))
        self.assertFalse(any(r["voice_class"] == "keeper_gloss" for r in rows))

    def test_voice_boundary_is_explicitly_mixed(self):
        self.manifest["documents"][0]["voice_segments"] = [
            {"start_marker": "Keeper note.", "voice_class": "keeper_testimony"},
            {"start_marker": "Witness dissent.", "voice_class": "witness_dissent"},
        ]
        rows = list(emit(self.root, self.manifest, size=19, overlap=0))
        self.assertTrue(any(r["voice_class"] == "mixed_voice_boundary" for r in rows))
        self.assertTrue(any(r["voice_class"] == "witness_dissent" for r in rows))
        self.assertFalse(any(r["voice_class"] == "keeper_testimony" and "Witness" in r["text"] for r in rows))

    def test_voice_marker_at_start_is_valid(self):
        self.manifest["documents"][0]["voice_segments"] = [
            {"start_marker": "Keeper note.", "voice_class": "keeper_testimony"},
            {"start_marker": "Witness dissent.", "voice_class": "witness_dissent"},
        ]
        rows = list(emit(self.root, self.manifest, size=12, overlap=0))
        self.assertEqual(rows[0]["voice_class"], "keeper_testimony")

    def test_missing_voice_marker_fails_closed(self):
        self.manifest["documents"][0]["voice_segments"] = [
            {"start_marker": "NONEXISTENT", "voice_class": "keeper_testimony"}
        ]
        with self.assertRaisesRegex(ValueError, "exactly once"):
            list(emit(self.root, self.manifest))

    def test_out_of_order_voice_markers_rejected(self):
        self.manifest["documents"][0]["voice_segments"] = [
            {"start_marker": "Witness dissent.", "voice_class": "witness_dissent"},
            {"start_marker": "Keeper note.", "voice_class": "keeper_testimony"},
        ]
        with self.assertRaisesRegex(ValueError, "ascending"):
            list(emit(self.root, self.manifest))

    def test_nonadvisory_manifest_rejected(self):
        self.manifest["status"] = "canon"
        with self.assertRaisesRegex(ValueError, "advisory"):
            list(emit(self.root, self.manifest))

    def test_invalid_windows(self):
        with self.assertRaises(ValueError):
            list(emit(self.root, self.manifest, size=0))

if __name__ == "__main__":
    unittest.main()
