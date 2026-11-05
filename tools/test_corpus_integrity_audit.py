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
            evidence = result["checksum"]["mismatch_evidence"]
            self.assertEqual(len(evidence), 1)
            self.assertEqual(evidence[0]["expected_sha256"], "0" * 64)
            self.assertEqual(evidence[0]["line"], 1)
            self.assertEqual(len(evidence[0]["checkout_sha256"]), 64)
            self.assertEqual(evidence[0]["resolution"], "unreviewed_no_automatic_rewrite")

    def test_missing_relative_link_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("[Missing](not-here.md)\n", encoding="utf-8")
            result = audit(root)
            self.assertEqual(result["missing_link_count"], 1)
            self.assertEqual(result["relative_markdown_links_missing"][0]["resolution"],
                             "candidate_requires_manual_review")

    def test_no_source_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "a.md"
            p.write_text("hello\n", encoding="utf-8")
            before = p.read_bytes()
            audit(root)
            self.assertEqual(p.read_bytes(), before)


    def test_empty_checksum_cannot_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "CHECKSUMS.sha256").write_text("", encoding="utf-8")
            self.assertTrue(audit(root)["checksum"]["empty"])

    def test_commented_checksum_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("changed", encoding="utf-8")
            (root / "CHECKSUMS.sha256").write_text("#" + "0" * 64 + "  a.md\\n", encoding="utf-8")
            result = audit(root)["checksum"]
            self.assertEqual(result["invalid_lines"], [1])
            self.assertTrue(result["empty"])

    def test_duplicate_checksum_path_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("data", encoding="utf-8")
            entry = "0" * 64 + "  a.md\\n"
            (root / "CHECKSUMS.sha256").write_text(entry + entry, encoding="utf-8")
            self.assertEqual(audit(root)["checksum"]["duplicate_paths"], ["a.md"])

    def test_missing_checksum_file_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = audit(tmp)["checksum"]
            self.assertTrue(result["checksum_file_missing"])
            self.assertTrue(result["empty"])

    def test_tracked_file_omitted_from_checksums_detected(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "a.md").write_text("data", encoding="utf-8")
            (root / "CHECKSUMS.sha256").write_text("", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "a.md", "CHECKSUMS.sha256"], check=True)
            self.assertIn("a.md", audit(root)["checksum"]["uncovered_tracked"])

    def test_archive_invariant_is_in_inventory(self):
        data = build(ROOT)
        self.assertIn("_ROOT_ARCHIVE/md/CANON_INVARIANTS.md",
                      {row["path"] for row in data["documents"]})


if __name__ == "__main__":
    unittest.main()
