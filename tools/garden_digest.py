#!/usr/bin/env python3
"""
tools/garden_digest.py

Creates a compact, high-signal snapshot of the Garden for agent ingestion.
Outputs:
  - EVOLUTION/garden_digest.json
  - EVOLUTION/garden_digest.md

Design goals:
  - Small enough for LLM prompts
  - Machine-readable + human-readable
  - Stable, deterministic ordering
"""
from __future__ import annotations

import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(".").resolve()

EXCLUDE_DIR_NAMES = {
    ".git", ".github", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache"
}

KEY_ANCHORS = [
    "AGENTS.md",
    "CANON_INVARIANTS.md",
    "PROTOCOL.md",
    "KEEPER_PROTOCOL.md",
    "CODEX_MEMORY.md",
    "STATUS.json",
    "STATUS.schema.json",
    "logs/aeon_heartbeat.json",
    "STATE/STATUS_v2.json",
    "GOLDEN_NULL_INDEX.md",
    "linked_index.json",
    "machine-index.json",
    "MACHINE-INDEX.json",
    "ORCHARD_MAPS.md",
    "THRESHOLD_MAP.md",
    "TRIAD_ATLAS.md",
]

TOP_DIRS_OF_INTEREST = [
    "EIDOLON",
    "CHAMBERS",
    "docs",
    "EVOLUTION",
    "ACACIA_SPECS",
    "ACACIA_LOGS",
    "ENTITIES",
    "ledger",
    "logs",
    "AQUILA",
]

TEXT_EXTS = {".md", ".txt", ".yml", ".yaml", ".json", ".py", ".js", ".mjs", ".ts", ".html", ".css"}

def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def iter_files():
    for root, dirs, files in os.walk(REPO_ROOT):
        # prune excluded dirs
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIR_NAMES]
        for fn in files:
            p = Path(root) / fn
            rel = p.relative_to(REPO_ROOT).as_posix()
            # skip gigantic binary-ish artifacts beyond extensions we care about
            yield p, rel

def build_digest(max_recent: int = 200, top_n_big: int = 40):
    now = datetime.now(timezone.utc).isoformat()
    counts_by_ext = {}
    counts_by_topdir = {d: 0 for d in TOP_DIRS_OF_INTEREST}
    total_files = 0
    big_files = []
    recent_files = []

    for p, rel in iter_files():
        total_files += 1
        ext = p.suffix.lower()
        counts_by_ext[ext] = counts_by_ext.get(ext, 0) + 1

        # top dir counts
        top = rel.split("/", 1)[0]
        if top in counts_by_topdir:
            counts_by_topdir[top] += 1

        try:
            st = p.stat()
        except FileNotFoundError:
            continue

        big_files.append((st.st_size, rel))
        recent_files.append((st.st_mtime, rel))

    big_files.sort(reverse=True, key=lambda x: x[0])
    recent_files.sort(reverse=True, key=lambda x: x[0])

    big_files = big_files[:top_n_big]
    recent_files = [r for _, r in recent_files[:max_recent]]

    anchors = []
    for a in KEY_ANCHORS:
        ap = (REPO_ROOT / a)
        anchors.append({
            "path": a,
            "exists": ap.exists(),
        })

    digest = {
        "generated_utc": now,
        "repo_root": str(REPO_ROOT),
        "total_files": total_files,
        "counts_by_extension": dict(sorted(counts_by_ext.items(), key=lambda kv: (-kv[1], kv[0]))),
        "counts_by_topdir": {k: counts_by_topdir[k] for k in TOP_DIRS_OF_INTEREST},
        "largest_files": [{"path": rel, "bytes": size} for size, rel in big_files],
        "most_recent_files": recent_files[:60],
        "key_anchors": anchors,
    }

    # small fingerprint: hash of anchor file hashes (only if exist & text-ish)
    anchor_hashes = []
    for a in KEY_ANCHORS:
        ap = (REPO_ROOT / a)
        if ap.exists() and ap.suffix.lower() in TEXT_EXTS:
            try:
                anchor_hashes.append((a, sha1_file(ap)))
            except Exception:
                pass
    anchor_hashes.sort(key=lambda x: x[0])
    digest["anchor_fingerprint_sha1"] = hashlib.sha1(
        ("\n".join([f"{p}:{h}" for p, h in anchor_hashes])).encode("utf-8")
    ).hexdigest()

    return digest

def write_outputs(digest: dict):
    evo_dir = REPO_ROOT / "EVOLUTION"
    evo_dir.mkdir(parents=True, exist_ok=True)

    json_path = evo_dir / "garden_digest.json"
    md_path = evo_dir / "garden_digest.md"

    json_path.write_text(json.dumps(digest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # markdown view (compact)
    lines = []
    lines.append("# GARDEN_DIGEST\n")
    lines.append(f"- Generated (UTC): **{digest['generated_utc']}**")
    lines.append(f"- Total files: **{digest['total_files']}**")
    lines.append(f"- Anchor fingerprint (sha1): `{digest['anchor_fingerprint_sha1']}`\n")

    lines.append("## Key anchors\n")
    for a in digest["key_anchors"]:
        mark = "✅" if a["exists"] else "❌"
        lines.append(f"- {mark} `{a['path']}`")

    lines.append("\n## Counts by top directory\n")
    for k, v in digest["counts_by_topdir"].items():
        lines.append(f"- `{k}/`: **{v} files**")

    lines.append("\n## Top file extensions (by count)\n")
    for ext, cnt in list(digest["counts_by_extension"].items())[:20]:
        ext_show = ext if ext else "(no ext)"
        lines.append(f"- `{ext_show}`: **{cnt}**")

    lines.append("\n## Largest files (top)\n")
    for item in digest["largest_files"][:25]:
        lines.append(f"- `{item['path']}` — {item['bytes']:,} bytes")

    lines.append("\n## Most recent paths (sample)\n")
    for rel in digest["most_recent_files"][:30]:
        lines.append(f"- `{rel}`")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main():
    digest = build_digest()
    write_outputs(digest)
    print("✅ Wrote EVOLUTION/garden_digest.json and EVOLUTION/garden_digest.md")

if __name__ == "__main__":
    main()
