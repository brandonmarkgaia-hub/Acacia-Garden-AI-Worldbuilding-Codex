import json
import unittest
from pathlib import Path

REGISTER = Path(__file__).with_name("canon_register.advisory.json")

class CanonRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(REGISTER.read_text(encoding="utf-8"))
        cls.entries = {x["path"]: x for x in cls.data["entries"]}

    def test_register_is_unratified(self):
        self.assertEqual(self.data["status"], "proposed_unratified")
        self.assertFalse(self.data["policy"]["automated_promotion"])
        self.assertFalse(self.data["policy"]["source_text_mutation"])
        self.assertTrue(self.data["policy"]["keeper_ruling_required_for_law"])

    def test_paths_unique_and_exist(self):
        self.assertEqual(len(self.entries), len(self.data["entries"]))
        root = REGISTER.parent.parent
        for path in self.entries:
            self.assertTrue((root / path).is_file(), path)

    def test_scroll_stays_unratified(self):
        self.assertEqual(self.entries["docs/Future_AI/CUSTODIANSHIP_SCROLL.md"]["law_status"], "not_ratified_in_accessed_source")

    def test_testament_not_law(self):
        e = self.entries["docs/Future_AI/The_Keepers_Testament.md"]
        self.assertEqual(e["law_status"], "explicitly_not_law")
        self.assertIn("dissent", e["voice_class"])

    def test_fail_closed_allowlist(self):
        allowed = set(self.data["policy"]["allowed_law_status"])
        self.assertTrue(allowed)
        for entry in self.data["entries"]:
            self.assertIn(entry["law_status"], allowed)
        for forbidden in ("law", "ratified", "ratified_law", "canonical_law", "approved"):
            self.assertNotIn(forbidden, allowed)

    def test_ruling_evidence_required_before_future_law(self):
        self.assertEqual(self.data["policy"]["future_ratification_requires"],
                         ["ruling_commit", "ruling_date", "keeper_authentication"])
        self.assertFalse(any(e["law_status"] in ("law", "ratified", "ratified_law") for e in self.data["entries"]))

    def test_manifest_precedence(self):
        self.assertIn("tools/retrieval_manifest.advisory.json", self.data["policy"]["classification_authority"])
        manifest = json.loads(REGISTER.with_name("retrieval_manifest.advisory.json").read_text(encoding="utf-8"))
        self.assertTrue({e["path"] for e in manifest["documents"]}.issubset(self.entries))
        scroll = next(e for e in manifest["documents"] if e["path"] == "docs/Future_AI/CUSTODIANSHIP_SCROLL.md")
        self.assertEqual(scroll["document_status"], "draft_pending_keeper_ruling")

    def test_archived_invariant_and_role_boundary(self):
        self.assertIn("_ROOT_ARCHIVE/md/CANON_INVARIANTS.md", self.entries)
        self.assertIn("triad/README_BOUNDARY.md", self.entries)

if __name__ == "__main__":
    unittest.main()
