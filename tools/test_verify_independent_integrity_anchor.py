"""Adversarial tests for the independent inventory verifier.

All signing keys here are ephemeral test fixtures, never authority credentials.
"""
import base64
import hashlib
import json
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from tools.verify_independent_integrity_anchor import canonical, verify

def digest(data):
    return hashlib.sha256(data).hexdigest()

class IndependentAnchorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "a.txt").write_text("original")
        (self.root / "b.txt").write_text("another")
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.root), "-c", "user.email=test@example.invalid",
                        "-c", "user.name=Fixture", "commit", "-qm", "fixture"], check=True)
        self.commit = subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True).strip()
        self.key = Ed25519PrivateKey.generate()
        self.now = int(time.time())
        self.inventory = {"repository": "fixture/example", "commit": self.commit, "exclusions": [],
                          "entries": [{"path": p, "sha256": digest((self.root / p).read_bytes())}
                                      for p in ("a.txt", "b.txt")]}
        self.statement = {"schema": "acacia.integrity-attestation/1", "repository": "fixture/example",
                          "commit": self.commit, "scope": "technical-integrity-only",
                          "challenge": "independent-reviewer-nonce-0123456789",
                          "issued_unix": self.now - 5, "expires_unix": self.now + 600, "exclusions": []}

    def sign(self, key=None):
        key = key or self.key
        inv = canonical(self.inventory)
        self.statement["inventory_sha256"] = digest(inv)
        public = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        attestation = {"statement": self.statement,
                       "public_key_b64": base64.b64encode(public).decode(),
                       "signature_b64": base64.b64encode(key.sign(canonical(self.statement))).decode()}
        return inv, canonical(attestation)

    def check(self, key=None):
        inv, att = self.sign(key)
        public = self.key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        return verify(self.root, inv, att, digest(public), self.now, self.commit)

    def test_valid_independently_matched_fixture(self):
        self.assertEqual(self.check()["checked"], 2)

    def test_tampered_file_rejected(self):
        (self.root / "a.txt").write_text("changed")
        with self.assertRaises(ValueError):
            self.check()

    def test_omitted_tracked_file_rejected(self):
        self.inventory["entries"].pop()
        with self.assertRaises(ValueError):
            self.check()

    def test_duplicate_path_rejected(self):
        self.inventory["entries"].append(dict(self.inventory["entries"][0]))
        with self.assertRaises(ValueError):
            self.check()

    def test_empty_inventory_rejected(self):
        self.inventory["entries"] = []
        with self.assertRaises(ValueError):
            self.check()

    def test_wrong_signer_rejected(self):
        with self.assertRaises(ValueError):
            self.check(Ed25519PrivateKey.generate())

    def test_expired_attestation_rejected(self):
        self.statement["expires_unix"] = self.now - 1
        with self.assertRaises(ValueError):
            self.check()

    def test_stale_commit_rejected(self):
        self.statement["commit"] = "0" * 40
        with self.assertRaises(ValueError):
            self.check()

    def test_unsigned_exclusion_rejected(self):
        self.inventory["exclusions"] = ["b.txt"]
        self.inventory["entries"].pop()
        with self.assertRaises(ValueError):
            self.check()

    def test_path_traversal_rejected(self):
        self.inventory["entries"][0]["path"] = "../outside"
        with self.assertRaises(ValueError):
            self.check()

    def test_external_repository_binding_rejected(self):
        inv, att = self.sign()
        pub = self.key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        with self.assertRaises(ValueError):
            verify(self.root, inv, att, digest(pub), self.now, self.commit,
                   expected_repository="other/repository")

    def test_external_challenge_binding_rejected(self):
        inv, att = self.sign()
        pub = self.key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        with self.assertRaises(ValueError):
            verify(self.root, inv, att, digest(pub), self.now, self.commit,
                   expected_challenge="independent-other-challenge-0123456789")

    def test_signed_exclusions_still_rejected_pending_policy(self):
        self.inventory["exclusions"] = ["b.txt"]
        self.inventory["entries"].pop()
        self.statement["exclusions"] = ["b.txt"]
        with self.assertRaises(ValueError):
            self.check()

    def test_malformed_digest_rejected(self):
        self.inventory["entries"][0]["sha256"] = "not-a-digest"
        with self.assertRaises(ValueError):
            self.check()

    def test_co_updated_content_and_inventory_without_external_signature_rejected(self):
        (self.root / "a.txt").write_text("tampered")
        inv, att = self.sign()
        self.inventory["entries"][0]["sha256"] = digest((self.root / "a.txt").read_bytes())
        with self.assertRaises(ValueError):
            verify(self.root, canonical(self.inventory), att,
                   digest(self.key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)),
                   self.now, self.commit)

if __name__ == "__main__":
    unittest.main()
