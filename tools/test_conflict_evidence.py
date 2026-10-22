import tempfile
import unittest
from pathlib import Path
from tools.conflict_evidence import review_candidates

class ConflictEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "a.md").write_text("Draft pending decision", encoding="utf-8")
        (self.root / "b.md").write_text("Agreed law", encoding="utf-8")
        self.spec = {"status": "advisory_not_canon", "candidates": [
            {"id": "status-disagreement", "hypothesis": "Status may conflict",
             "evidence": [{"path": "a.md", "exact_anchor": "Draft"},
                          {"path": "b.md", "exact_anchor": "Agreed"}]}
        ]}

    def test_exact_evidence_and_no_authority(self):
        candidate = list(review_candidates(self.root, self.spec))[0]
        self.assertEqual(candidate["decision"], "human_review_required")
        self.assertFalse(candidate["truth_decided"])
        self.assertFalse(candidate["canon_authorized"])
        self.assertEqual(candidate["evidence"][0]["start_offset"], 0)

    def test_missing_anchor_fails_closed(self):
        self.spec["candidates"][0]["evidence"][1]["exact_anchor"] = "Not present"
        with self.assertRaisesRegex(ValueError, "exactly once"):
            list(review_candidates(self.root, self.spec))

    def test_ambiguous_anchor_fails_closed(self):
        (self.root / "a.md").write_text("Draft Draft", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "exactly once"):
            list(review_candidates(self.root, self.spec))

    def test_two_distinct_sources_required(self):
        self.spec["candidates"][0]["evidence"][1]["path"] = "a.md"
        with self.assertRaisesRegex(ValueError, "different sources"):
            list(review_candidates(self.root, self.spec))

    def test_canon_status_rejected(self):
        self.spec["status"] = "canon"
        with self.assertRaisesRegex(ValueError, "advisory"):
            list(review_candidates(self.root, self.spec))

    def test_path_traversal_rejected(self):
        self.spec["candidates"][0]["evidence"][0]["path"] = "../outside.md"
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            list(review_candidates(self.root, self.spec))

if __name__ == "__main__":
    unittest.main()
