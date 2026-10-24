#!/usr/bin/env python3
"""Read-only, checkout-bound ten-path checksum and git-history evidence."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = [
    "STATUS.json",
    "docs/Chambers/chambers_index.json",
    "docs/Chambers/index.html",
    "docs/Echoes/echoes_index.json",
    "docs/Echoes/index.html",
    "docs/GardenOS/index.html",
    "docs/Novellas/garden_index.json",
    "docs/Vaults/index.html",
    "docs/docs_urls.json",
    "machine-index.json",
]

def run_git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()

def build():
    entries = {}
    for n, line in enumerate((ROOT / "CHECKSUMS.sha256").read_text().splitlines(), 1):
        if "  " not in line:
            continue
        digest, path = line.split("  ", 1)
        entries[path.lstrip("*")] = (n, digest.lower())
    records = []
    for name in PATHS:
        if name not in entries:
            raise ValueError("Checksum entry missing: " + name)
        target = ROOT / name
        line, expected = entries[name]
        actual = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
        history = run_git("log", "-1", "--format=%H%x09%cI%x09%s", "--", name).split("\t", 2)
        records.append({
            "path": name,
            "checksum_line": line,
            "expected_sha256": expected,
            "checkout_sha256": actual,
            "match": actual == expected,
            "last_modifying_commit": history[0] if len(history) == 3 else None,
            "last_modifying_date": history[1] if len(history) == 3 else None,
            "last_modifying_subject": history[2] if len(history) == 3 else None,
            "disposition": "requires_independent_review",
        })
    return {
        "schema": "acacia.checksum-provenance/1",
        "checkout_head": run_git("rev-parse", "HEAD"),
        "checksum_file_sha256": hashlib.sha256((ROOT / "CHECKSUMS.sha256").read_bytes()).hexdigest(),
        "status": "advisory_not_keeper_attestation",
        "findings": records,
    }

if __name__ == "__main__":
    report = build()
    print(json.dumps(report, indent=2))
    Path("/tmp/diamond-checksum-provenance.json").write_text(json.dumps(report, indent=2) + "\n")
