import tempfile
import unittest
from pathlib import Path

from tools.conflict_review_register import evaluate

class ReviewRegisterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "a.md").write_text("Provisional rule", encoding="utf-8")
        (self.root / "b.md").write_text("Later amendment", encoding="utf-8")
        self.spec = {"status": "advisory_not_canon", "candidates": [
            {"id": "C1", "hypothesis": "Possible chronology conflict",
             "evidence": [{"path": "a.md", "exact_anchor": "Provisional rule"},
                          {"path": "b.md", "exact_anchor": "Later amendment"}]}
        ]}

    def test_review_state_never_decides_truth(self):
        r = evaluate(self.root, self.spec)[0]
        self.assertEqual(r["classification"], "unresolved_pending_human_review")
        self.assertFalse(r["canon_authorized"])
        self.assertFalse(r["truth_decided"])

    def test_duplicate_ids_rejected(self):
        self.spec["candidates"].append(dict(self.spec["candidates"][0]))
        with self.assertRaisesRegex(ValueError, "unique"):
            evaluate(self.root, self.spec)

    def test_empty_hypothesis_rejected(self):
        self.spec["candidates"][0]["hypothesis"] = ""
        with self.assertRaisesRegex(ValueError, "hypothesis"):
            evaluate(self.root, self.spec)

    def test_missing_evidence_rejected(self):
        self.spec["candidates"][0]["evidence"][0]["exact_anchor"] = "Not present"
        with self.assertRaisesRegex(ValueError, "exactly once"):
            evaluate(self.root, self.spec)

if __name__ == "__main__":
    unittest.main()
