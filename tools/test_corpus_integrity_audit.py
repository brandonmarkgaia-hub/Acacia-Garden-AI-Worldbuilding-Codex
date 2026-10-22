import json
import tempfile
import unittest
from pathlib import Path

from tools.corpus_integrity_audit import audit
from tools.exhaustive_canon_inventory import build

ROOT = Path(__file__).resolve().parent.parent


class CorpusAuditTests(unittest.TestCase):
    def test_exhaustive_inventory_is_non_authorizing(self):
        data = build(ROOT)
        self.assertEqual(data["status"], "advisory_not_canon")
        self.assertGreater(data["count"], 100)
        self.assertEqual(data["count"], data["reviewed_count"] + data["unknown_count"])
        self.assertTrue(all(row["law_authorized"] is False for row in data["documents"]))
        scroll = next(row for row in data["documents"] if row["path"] == "docs/Future_AI/CUSTODIANSHIP_SCROLL.md")
        self.assertFalse(scroll["section_specific_claim"]["whole_document_law_authorized"])

    def test_checksum_mismatch_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("# Test\n", encoding="utf-8")
            (root / "CHECKSUMS.sha256").write_text("0" * 64 + "  a.md\n", encoding="utf-8")
            result = audit(root)
            self.assertEqual(result["checksum"]["mismatches"], ["a.md"])

    def test_no_source_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "a.md"
            p.write_text("hello\n", encoding="utf-8")
            before = p.read_bytes()
            audit(root)
            self.assertEqual(p.read_bytes(), before)

    def test_archive_invariant_is_in_inventory(self):
        data = build(ROOT)
        self.assertIn("_ROOT_ARCHIVE/md/CANON_INVARIANTS.md",
                      {row["path"] for row in data["documents"]})


if __name__ == "__main__":
    unittest.main()
