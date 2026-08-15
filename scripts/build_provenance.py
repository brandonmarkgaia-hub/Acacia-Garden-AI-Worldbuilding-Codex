#!/usr/bin/env python3
"""Build deterministic Acacia Garden repository provenance artifacts."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKSUMS = ROOT / "CHECKSUMS.sha256"
VERSION = ROOT / "GARDEN_VERSION.json"
EXCLUDE = {"CHECKSUMS.sha256", "GARDEN_VERSION.json"}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tracked_files() -> list[str]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return sorted(p.decode("utf-8") for p in raw.split(b"\0") if p)


def main() -> int:
    commit = git("rev-parse", "HEAD")
    tree = git("rev-parse", "HEAD^{tree}")
    commit_time = git("show", "-s", "--format=%cI", "HEAD")
    paths = [p for p in tracked_files() if p not in EXCLUDE and (ROOT / p).is_file()]

    lines: list[str] = []
    hashes: dict[str, str] = {}
    for rel in paths:
        digest = sha256(ROOT / rel)
        hashes[rel] = digest
        lines.append(f"{digest}  {rel}")
    CHECKSUMS.write_text("\n".join(lines) + "\n", encoding="utf-8")

    critical = [
        "AUTHORITY.json",
        "README.md",
        "DISCOVERY.md",
        "llms.txt",
        "llms-full.txt",
        "AGENTS.md",
        "STATUS.json",
        "machine-index.json",
        "machine-discovery.json",
        ".well-known/acacia.json",
        "robots.txt",
        "sitemap.xml",
    ]
    html_count = sum(1 for p in paths if p.lower().endswith((".html", ".htm")))
    payload = {
        "schema": "acacia.repository-state/1.0",
        "purpose": "Machine-verifiable identity and integrity metadata for one Git repository state. This file does not define canon or authority.",
        "repository": "https://github.com/brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex",
        "git": {
            "commit": commit,
            "tree": tree,
            "commit_time": commit_time,
            "default_branch": "main",
        },
        "authority_source": "AUTHORITY.json",
        "integrity": {
            "algorithm": "sha256",
            "manifest": "CHECKSUMS.sha256",
            "tracked_files_hashed": len(paths),
            "html_files_hashed": html_count,
            "excluded_self_referential_outputs": sorted(EXCLUDE),
        },
        "critical_surface_sha256": {
            rel: hashes[rel] for rel in critical if rel in hashes
        },
        "interpretation": {
            "git_is_provenance_record": True,
            "hash_match_means_byte_identity_not_canonical_authority": True,
            "authority_must_be_resolved_via": "AUTHORITY.json",
        },
    }
    VERSION.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {CHECKSUMS.relative_to(ROOT)} with {len(paths)} hashes")
    print(f"Wrote {VERSION.relative_to(ROOT)} for commit {commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
