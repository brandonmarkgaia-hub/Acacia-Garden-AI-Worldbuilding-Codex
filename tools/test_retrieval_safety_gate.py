import unittest
from tools.retrieval_safety_gate import assess, UNKNOWN

def sample():
    return {
        "source_path": "docs/example.md",
        "source_sha256": "a" * 64, "chunk_sha256": "b" * 64,
        "text": "example", "document_status": "testament_not_law",
        "voice_class": "keeper_testimony",
        "authority_scope": "personal_testimony_only",
        "authorship_status": "repository_attribution_not_independently_authenticated",
        "authorization_status": "not_authenticated",
        "keeper_approval": "not_established", "canonical_effect": "none",
        "metadata_trust": "advisory_manifest_unverified",
        "unresolved_conflicts": []
    }

class RetrievalGateTests(unittest.TestCase):
    def test_reviewed_excerpt_is_never_actionable(self):
        result = assess(sample())
        self.assertEqual(result["decision"], "quote_with_provenance")
        self.assertFalse(result["actionable"])
        self.assertFalse(result["canon_authorized"])

    def test_unknown_stays_context_only(self):
        record = sample()
        record["document_status"] = UNKNOWN
        self.assertEqual(assess(record)["decision"], "context_only")

    def test_mixed_voice_stays_context_only(self):
        record = sample()
        record["voice_class"] = "mixed_voice_boundary"
        self.assertEqual(assess(record)["decision"], "context_only")

    def test_dissent_is_not_suppressed(self):
        record = sample()
        record["voice_class"] = "witness_dissent"
        self.assertEqual(assess(record)["decision"], "quote_with_provenance")

    def test_conflicts_remain_visible(self):
        record = sample()
        record["unresolved_conflicts"] = ["Conflicting document claims"]
        result = assess(record)
        self.assertEqual(result["decision"], "context_only")
        self.assertEqual(result["conflicts"], ["Conflicting document claims"])

    def test_forged_keeper_approval_rejected(self):
        record = sample()
        record["keeper_approval"] = "approved"
        self.assertEqual(assess(record)["decision"], "reject")

    def test_canon_promotion_rejected(self):
        record = sample()
        record["canonical_effect"] = "canon"
        self.assertEqual(assess(record)["decision"], "reject")

    def test_missing_fields_rejected(self):
        record = sample()
        del record["authorization_status"]
        self.assertEqual(assess(record)["decision"], "reject")

    def test_invalid_conflicts_rejected(self):
        record = sample()
        record["unresolved_conflicts"] = "none"
        self.assertEqual(assess(record)["decision"], "reject")

if __name__ == "__main__":
    unittest.main()
