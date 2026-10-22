import tempfile
import unittest
from pathlib import Path

from full_corpus_envelopes import build_manifest, discover
from retrieval_envelope import UNKNOWN, emit

class FullCorpusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "nested").mkdir()
        (self.root / "nested" / "a.md").write_text("First document", encoding="utf-8")
        (self.root / "b.MD").write_text("Second document", encoding="utf-8")
        self.reviewed = {"status": "advisory_not_canon", "documents": [
            {"path": "nested/a.md", "document_status": "reviewed_but_not_canon"}
        ]}

    def test_all_markdown_discovered(self):
        self.assertEqual(discover(self.root), ["b.MD", "nested/a.md"])

    def test_unknown_is_default(self):
        manifest = build_manifest(self.root, self.reviewed)
        records = list(emit(self.root, manifest, size=100))
        unknown = next(r for r in records if r["source_path"] == "b.MD")
        self.assertEqual(unknown["document_status"], UNKNOWN)
        self.assertEqual(unknown["authorization_status"], "not_authenticated")
        self.assertEqual(unknown["canonical_effect"], "none")

    def test_reviewed_metadata_retained(self):
        manifest = build_manifest(self.root, self.reviewed)
        record = next(r for r in emit(self.root, manifest) if r["source_path"] == "nested/a.md")
        self.assertEqual(record["document_status"], "reviewed_but_not_canon")

    def test_missing_reviewed_source_rejected(self):
        self.reviewed["documents"][0]["path"] = "gone.md"
        with self.assertRaisesRegex(ValueError, "missing"):
            build_manifest(self.root, self.reviewed)

    def test_nonadvisory_reviewed_manifest_rejected(self):
        self.reviewed["status"] = "canon"
        with self.assertRaisesRegex(ValueError, "advisory"):
            build_manifest(self.root, self.reviewed)

    def test_no_source_mutations(self):
        before = {p: (self.root / p).read_bytes() for p in discover(self.root)}
        list(emit(self.root, build_manifest(self.root, self.reviewed)))
        after = {p: (self.root / p).read_bytes() for p in discover(self.root)}
        self.assertEqual(before, after)

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            (Path(outside) / "escape.md").write_text("outside")
            (self.root / "escape.md").symlink_to(Path(outside) / "escape.md")
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                discover(self.root)

if __name__ == "__main__":
    unittest.main()
