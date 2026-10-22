import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "keeper_final_seal.advisory.json").read_text(encoding="utf-8"))

class KeeperFinalSealTests(unittest.TestCase):
    def test_dormant(self):
        self.assertEqual(DATA["status"], "proposed_dormant")
        self.assertFalse(DATA["activation"]["seal_active"])
        self.assertFalse(DATA["activation"]["automatic_activation"])
        self.assertEqual(DATA["activation"]["verification_procedure"], "not_yet_established")

    def test_no_premature_frozen_commit(self):
        self.assertIsNone(DATA["frozen_commit"])
        self.assertIsNone(DATA["archive_manifest_sha256"])
        self.assertIsNone(DATA["trusted_keeper_attestation"])

    def test_original_reference(self):
        self.assertEqual(DATA["keeper_identifier"], "HKX277206")
        self.assertEqual(DATA["original_repository"], "https://github.com/brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex")

    def test_descendants_free_but_original_protected(self):
        d = DATA["descendant_requirements"]
        self.assertTrue(d["new_branches_and_forks"])
        self.assertTrue(d["new_repositories"])
        self.assertFalse(d["edit_sealed_original"])
        self.assertFalse(d["delete_sealed_original"])
        self.assertTrue(d["independent_authorship_and_provenance"])

    def test_council_no_rewrite(self):
        self.assertEqual(DATA["future_deliberation"]["roles"], ["advocate", "challenger", "witness"])
        self.assertFalse(DATA["future_deliberation"]["may_rewrite_sealed_archive"])

if __name__ == "__main__":
    unittest.main()
