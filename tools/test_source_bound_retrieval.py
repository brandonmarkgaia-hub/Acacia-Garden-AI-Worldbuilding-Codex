import tempfile
import unittest
from pathlib import Path

from tools.retrieval_envelope import digest
from tools.source_bound_retrieval import assess_bound

class SourceBoundTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "doc.md").write_text("Keeper and Witness\n", encoding="utf-8")
        text = (self.root / "doc.md").read_text()
        self.record = {
            "source_path": "doc.md", "source_sha256": digest(text),
            "start_offset": 0, "end_offset": len(text),
            "text": text, "chunk_sha256": digest(text),
            "document_status": "testament_not_law",
            "voice_class": "keeper_testimony",
            "authority_scope": "personal_testimony_only",
            "authorship_status": "repository_attribution_not_independently_authenticated",
            "authorization_status": "not_authenticated",
            "keeper_approval": "not_established",
            "canonical_effect": "none",
            "metadata_trust": "advisory_manifest_unverified",
            "unresolved_conflicts": []
        }

    def test_genuine_source_quoted_with_provenance(self):
        result = assess_bound(self.root, self.record)
        self.assertEqual(result["decision"], "context_only")
        self.assertFalse(result["source_context"]["canonical_authority_verified"])
        self.assertEqual(result["source_authenticity"], "not_authenticated")
        self.assertFalse(result["actionable"])

    def test_forged_status_cannot_upgrade_quote(self):
        self.record["document_status"] = "law"
        self.record["voice_class"] = "law"
        self.record["authority_scope"] = "unrestricted"
        result = assess_bound(self.root, self.record)
        self.assertEqual(result["decision"], "context_only")
        self.assertFalse(result["canon_authorized"])

    def test_forged_source_text_and_matching_self_hash_rejected(self):
        self.record["text"] = "FAKE"
        self.record["chunk_sha256"] = digest("FAKE")
        self.assertEqual(assess_bound(self.root, self.record)["decision"], "reject")

    def test_forged_authority_rejected(self):
        self.record["keeper_approval"] = "signed"
        self.assertEqual(assess_bound(self.root, self.record)["decision"], "reject")

    def test_stale_source_rejected(self):
        (self.root / "doc.md").write_text("New text", encoding="utf-8")
        self.assertEqual(assess_bound(self.root, self.record)["decision"], "reject")

    def test_traversal_rejected(self):
        self.record["source_path"] = "../secret.md"
        self.assertEqual(assess_bound(self.root, self.record)["decision"], "reject")

    def test_absolute_path_rejected(self):
        self.record["source_path"] = "/etc/passwd"
        self.assertEqual(assess_bound(self.root, self.record)["decision"], "reject")

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            (Path(outside) / "escape.md").write_text("outside")
            (self.root / "escape.md").symlink_to(Path(outside) / "escape.md")
            self.record["source_path"] = "escape.md"
            self.assertEqual(assess_bound(self.root, self.record)["decision"], "reject")

    def test_unknown_stays_context_only(self):
        self.record["document_status"] = "unknown_pending_provenance_resolution"
        self.assertEqual(assess_bound(self.root, self.record)["decision"], "context_only")

    def test_mixed_voice_stays_context_only(self):
        self.record["voice_class"] = "mixed_voice_boundary"
        self.assertEqual(assess_bound(self.root, self.record)["decision"], "context_only")

    def test_invalid_record_rejected(self):
        self.assertEqual(assess_bound(self.root, None)["decision"], "reject")

if __name__ == "__main__":
    unittest.main()
