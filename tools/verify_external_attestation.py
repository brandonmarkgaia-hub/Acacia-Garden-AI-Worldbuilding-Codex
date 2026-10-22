#!/usr/bin/env python3
"""Fail-closed external attestation verifier.

The public key must be supplied from a trusted channel outside the repository.
An attestation file in the repo is never itself sufficient evidence of identity.
Uses OpenSSL CLI for Ed25519 verification; no key creation or approval inference.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")

def canonical_statement(repo, commit, scope):
    if not isinstance(repo, str) or not repo or "\n" in repo:
        raise ValueError("Invalid repository")
    if not isinstance(commit, str) or not SHA.fullmatch(commit):
        raise ValueError("Invalid commit")
    if not isinstance(scope, str) or scope not in ("integrity_acknowledgment", "keeper_reviewed_release"):
        raise ValueError("Invalid attestation scope")
    return (json.dumps({"schema": "acacia.attestation/1", "repository": repo,
                        "commit": commit, "scope": scope},
                       sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()

def verify_statement(public_key_path, signature_path, statement_path):
    proc = subprocess.run(["openssl", "pkeyutl", "-verify", "-pubin",
                           "-inkey", str(public_key_path), "-sigfile",
                           str(signature_path), "-rawin", "-in",
                           str(statement_path)], capture_output=True, text=True)
    return proc.returncode == 0

def verify_claim(repo, commit, scope, trusted_public_key, signature, signed_statement):
    expected = canonical_statement(repo, commit, scope)
    if Path(signed_statement).read_bytes() != expected:
        return False
    return verify_statement(trusted_public_key, signature, signed_statement)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repository", required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--scope", required=True)
    p.add_argument("--trusted-public-key", required=True,
                   help="Trusted out-of-band public key, NOT automatically trusted from repo")
    p.add_argument("--signature", required=True)
    p.add_argument("--statement", required=True)
    a = p.parse_args()
    verified = verify_claim(a.repository, a.commit, a.scope,
                            a.trusted_public_key, a.signature, a.statement)
    print(json.dumps({"signature_valid_for_supplied_key": verified,
                      "key_identity_verified": False,
                      "keeper_approval_established": False,
                      "note": "Key ownership and authorization require independent verification"}))
    if not verified:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
