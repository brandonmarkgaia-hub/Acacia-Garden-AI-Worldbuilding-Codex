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

    def test_no_unverified_law_promotion(self):
        for entry in self.data["entries"]:
            self.assertNotEqual(entry["law_status"], "ratified_law")

if __name__ == "__main__":
    unittest.main()
