#!/usr/bin/env python3
"""Offline, read-only verification of an externally signed current inventory.

The expected signer fingerprint must come from an independent trusted channel.
This tool cannot establish that provenance, Keeper identity, or canon authority.
"""
import argparse
import base64
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def verify(root, inventory_bytes, attestation_bytes, expected_fingerprint, now, expected_commit,
           expected_repository=None, expected_challenge=None):
    root = Path(root).resolve()
    inventory = json.loads(inventory_bytes)
    attestation = json.loads(attestation_bytes)
    statement = attestation["statement"]
    pub = base64.b64decode(attestation["public_key_b64"], validate=True)
    signature = base64.b64decode(attestation["signature_b64"], validate=True)
    fingerprint = sha256(pub)
    if len(pub) != 32 or fingerprint != expected_fingerprint:
        raise ValueError("Signer fingerprint not independently matched")
    Ed25519PublicKey.from_public_bytes(pub).verify(signature, canonical(statement))
    if statement.get("schema") != "acacia.integrity-attestation/1":
        raise ValueError("Unsupported attestation schema")
    if statement.get("inventory_sha256") != sha256(inventory_bytes):
        raise ValueError("Inventory differs from signed digest")
    if statement.get("commit") != expected_commit or inventory.get("commit") != expected_commit:
        raise ValueError("Commit binding mismatch")
    if statement.get("expires_unix", 0) <= now or statement.get("issued_unix", now + 1) > now:
        raise ValueError("Attestation expired or issued in future")
    if not isinstance(statement.get("challenge"), str) or len(statement["challenge"]) < 24:
        raise ValueError("Missing reviewer challenge")
    if not statement.get("repository"):
        raise ValueError("Missing repository binding")
    if statement.get("repository") != inventory.get("repository"):
        raise ValueError("Repository binding mismatch")
    if statement.get("scope") != "technical-integrity-only":
        raise ValueError("Unsupported authority scope")
    entries = inventory.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Missing inventory entries")
    tracked_raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
    tracked = {x.decode("utf-8") for x in tracked_raw.split(b"\x00") if x}
    exclusions = inventory.get("exclusions", [])
    if not isinstance(exclusions, list) or any(not isinstance(x, str) for x in exclusions):
        raise ValueError("Invalid exclusions")
    if set(exclusions) != set(statement.get("exclusions", [])):
        raise ValueError("Exclusions not signed")
    if len(exclusions) != len(set(exclusions)) or not set(exclusions) <= tracked:
        raise ValueError("Invalid excluded paths")
    seen = set()
    for entry in entries:
        path = entry.get("path")
        digest = entry.get("sha256")
        if not isinstance(path, str) or not isinstance(digest, str):
            raise ValueError("Invalid inventory entry")
        pure = PurePosixPath(path)
        if path.startswith("/") or "\\" in path or ".." in pure.parts or path != pure.as_posix():
            raise ValueError("Unsafe path")
        if path in seen:
            raise ValueError("Duplicate path")
        seen.add(path)
        file = root / path
        if file.is_symlink() or not file.is_file():
            raise ValueError("Missing or symlinked file")
        if sha256(file.read_bytes()) != digest:
            raise ValueError("Content mismatch: " + path)
    if seen != tracked - set(exclusions):
        raise ValueError("Incomplete tracked-file coverage")
    dirty = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"])
    if dirty:
        raise ValueError("Tracked checkout is dirty")
    actual_commit = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if actual_commit != expected_commit:
        raise ValueError("Checkout differs from attested commit")
    return {"status": "technical_inventory_verified", "commit": actual_commit,
            "checked": len(seen), "excluded": len(exclusions),
            "signer_fingerprint_sha256": fingerprint,
            "limitations": ["Independent provenance of expected fingerprint must be established externally",
                            "Challenge uniqueness and replay prevention require external reviewer state",
                            "No Keeper or canon authority established"]}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--inventory", required=True)
    p.add_argument("--attestation", required=True)
    p.add_argument("--expected-signer-sha256", required=True)
    p.add_argument("--expected-commit", required=True)
    p.add_argument("--now-unix", type=int, required=True)
    p.add_argument("--expected-repository", required=True)
    p.add_argument("--expected-challenge", required=True)
    a = p.parse_args()
    result = verify(a.root, Path(a.inventory).read_bytes(), Path(a.attestation).read_bytes(),
                    a.expected_signer_sha256, a.now_unix, a.expected_commit,
                    a.expected_repository, a.expected_challenge)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
