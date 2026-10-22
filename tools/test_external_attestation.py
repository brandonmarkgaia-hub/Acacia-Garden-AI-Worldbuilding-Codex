import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from tools.verify_external_attestation import canonical_statement, verify_claim

REPO = "brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex"
COMMIT = "a" * 40

class AttestationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.private = self.root / "private.pem"
        self.public = self.root / "public.pem"
        self.statement = self.root / "statement.json"
        self.signature = self.root / "statement.sig"
        subprocess.run(["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(self.private)], check=True, capture_output=True)
        subprocess.run(["openssl", "pkey", "-in", str(self.private), "-pubout", "-out", str(self.public)], check=True, capture_output=True)
        self.statement.write_bytes(canonical_statement(REPO, COMMIT, "integrity_acknowledgment"))
        subprocess.run(["openssl", "pkeyutl", "-sign", "-inkey", str(self.private), "-rawin",
                        "-in", str(self.statement), "-out", str(self.signature)], check=True, capture_output=True)

    def check(self, commit=COMMIT, scope="integrity_acknowledgment"):
        return verify_claim(REPO, commit, scope, self.public, self.signature, self.statement)

    def test_valid_signature_for_supplied_key(self):
        self.assertTrue(self.check())

    def test_different_commit_rejected(self):
        self.assertFalse(self.check("b" * 40))

    def test_different_scope_rejected(self):
        self.assertFalse(self.check(scope="keeper_reviewed_release"))

    def test_tampered_statement_rejected(self):
        self.statement.write_bytes(self.statement.read_bytes() + b" ")
        self.assertFalse(self.check())

    def test_tampered_signature_rejected(self):
        self.signature.write_bytes(b"not a signature")
        self.assertFalse(self.check())

    def test_wrong_key_rejected(self):
        wrong = self.root / "wrong.pem"
        other = self.root / "other.pem"
        subprocess.run(["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(other)], check=True, capture_output=True)
        subprocess.run(["openssl", "pkey", "-in", str(other), "-pubout", "-out", str(wrong)], check=True, capture_output=True)
        self.assertFalse(verify_claim(REPO, COMMIT, "integrity_acknowledgment", wrong, self.signature, self.statement))

    def test_bad_commit_rejected(self):
        with self.assertRaises(ValueError):
            canonical_statement(REPO, "main", "integrity_acknowledgment")

    def test_bad_scope_rejected(self):
        with self.assertRaises(ValueError):
            canonical_statement(REPO, COMMIT, "grant_all_canon")

if __name__ == "__main__":
    unittest.main()
