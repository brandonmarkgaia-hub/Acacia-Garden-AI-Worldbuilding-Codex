#!/usr/bin/env python3
"""Generate or verify a scoped, versioned current-release manifest.

CHECKSUMS.sha256 remains an untouched historical evidence snapshot.
No source, authority, or archive content is changed by this tool.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "releases" / "CURRENT_RELEASE_MANIFEST.v1.json"
EXCLUDED = {"CHECKSUMS.sha256", "releases/CURRENT_RELEASE_MANIFEST.v1.json"}


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def manifest():
    paths = git("ls-files", "-z").split("\0")
    files = []
    for rel in sorted(filter(None, paths)):
        if rel in EXCLUDED:
            continue
        path = ROOT / rel
        if not path.is_file() or path.is_symlink():
            raise ValueError("Tracked file absent or symlink (not silently omitted): " + rel)
        data = path.read_bytes()
        files.append({"path": rel, "sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data)})
    return {
        "schema": "acacia.current-release-manifest/1",
        "scope": "git tracked regular files, excluding historical CHECKSUMS.sha256 and this manifest",
        "checkout_commit": git("rev-parse", "HEAD"),
        "historical_checksum_sha256": hashlib.sha256((ROOT / "CHECKSUMS.sha256").read_bytes()).hexdigest(),
        "status": "technical_evidence_only_not_keeper_attestation",
        "entries": files,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write manifest for review; does not modify historical checksums")
    ap.add_argument("--verify", action="store_true", help="Compare all recorded hashes and scope against current tracked checkout")
    args = ap.parse_args()
    if args.write == args.verify:
        ap.error("Choose exactly one of --write or --verify")
    current = manifest()
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {len(current['entries'])} tracked-file hashes to {OUT}")
        return
    recorded = json.loads(OUT.read_text(encoding="utf-8"))
    # Commit identity changes when a manifest is committed. Checksum content,
    # scope and file hashes are the actual verification criteria.
    for field in ("schema", "scope", "historical_checksum_sha256", "entries"):
        if recorded.get(field) != current[field]:
            raise SystemExit("FAIL: current-release manifest differs in " + field)
    print(f"PASS: {len(current['entries'])} tracked file hashes and historical checksum identity")


if __name__ == "__main__":
    main()
