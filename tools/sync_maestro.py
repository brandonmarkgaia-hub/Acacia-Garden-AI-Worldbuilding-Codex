#!/usr/bin/env python3
"""
tools/sync_maestro.py

Index Coherence + Temporal Synchronization helper.
Outputs:
  - STATE/index_authority.json   (declares canonical files, duplicates, and advice)
  - ACACIA_LOGS/sync_report_YYYYMMDD.md

This tool is *non-destructive*. It does NOT delete or rename anything.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(".").resolve()

KNOWN_INDEX_CANDIDATES = [
    "machine-index.json",
    "MACHINE-INDEX.json",
    "linked_index.json",
    "GOLDEN_NULL_INDEX.md",
    "EVOLUTION/garden_digest.json",
    "EVOLUTION/garden_digest.md",
    "ORCHARD_MAPS.md",
    "THRESHOLD_MAP.md",
    "TRIAD_ATLAS.md",
    "logs/aeon_heartbeat.json",
    "STATUS.json",
    "STATE/STATUS_v2.json",
]

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def extract_timestamp_any(obj):
    """
    Heuristic timestamp extraction used for coherence checks.
    Accepts dict/str and looks for ISO-ish stamps.
    """
    if isinstance(obj, dict):
        for k in ["generated_utc", "timestamp", "last_cycle_stamp", "cycle_start_time", "updated_utc"]:
            v = obj.get(k)
            if isinstance(v, str):
                return v
    if isinstance(obj, str):
        # simple ISO match
        m = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", obj)
        if m:
            return m.group(0)
    return None

def pick_canonical_machine_index():
    lower = REPO / "machine-index.json"
    upper = REPO / "MACHINE-INDEX.json"
    if lower.exists() and upper.exists():
        # Prefer lower-case as canonical (linux-friendly + consistent)
        return "machine-index.json", ["MACHINE-INDEX.json"]
    if lower.exists():
        return "machine-index.json", []
    if upper.exists():
        return "MACHINE-INDEX.json", []
    return None, []

def build_authority():
    now = datetime.now(timezone.utc).isoformat()

    canonical_machine_index, legacy_dupes = pick_canonical_machine_index()
    present = []
    missing = []
    meta = {}

    for rel in KNOWN_INDEX_CANDIDATES:
        p = REPO / rel
        if p.exists():
            present.append(rel)
        else:
            missing.append(rel)

        if p.exists() and p.suffix.lower() == ".json":
            data = read_json(p)
            ts = extract_timestamp_any(data) if data else None
            meta[rel] = {"timestamp": ts, "ok_json": bool(data)}
        else:
            meta[rel] = {"timestamp": None}

    authority = {
        "generated_utc": now,
        "canonical": {
            "machine_index": canonical_machine_index,
            "status": "STATUS.json" if (REPO/"STATUS.json").exists() else None,
            "status_schema": "STATUS.schema.json" if (REPO/"STATUS.schema.json").exists() else None,
            "heartbeat": "logs/aeon_heartbeat.json" if (REPO/"logs/aeon_heartbeat.json").exists() else None,
            "golden_null_index": "GOLDEN_NULL_INDEX.md" if (REPO/"GOLDEN_NULL_INDEX.md").exists() else None,
            "threshold_map": "THRESHOLD_MAP.md" if (REPO/"THRESHOLD_MAP.md").exists() else None,
            "orchard_maps": "ORCHARD_MAPS.md" if (REPO/"ORCHARD_MAPS.md").exists() else None,
            "digest_json": "EVOLUTION/garden_digest.json" if (REPO/"EVOLUTION/garden_digest.json").exists() else None,
        },
        "legacy_or_duplicate_candidates": legacy_dupes,
        "present_candidates": sorted(present),
        "missing_candidates": sorted(missing),
        "candidate_metadata": meta,
        "guidance": [
            "Treat STATE/index_authority.json as the single source-of-truth for which index files are canonical.",
            "Prefer proposal-only state updates (STATE/STATUS_v*.json) rather than overwriting STATUS.json automatically.",
            "Avoid creating new parallel indices unless they are explicitly added to index_authority.json.",
        ],
    }
    return authority

def write_outputs(authority: dict):
    (REPO / "STATE").mkdir(parents=True, exist_ok=True)
    (REPO / "ACACIA_LOGS").mkdir(parents=True, exist_ok=True)

    auth_path = REPO / "STATE" / "index_authority.json"
    auth_path.write_text(json.dumps(authority, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    report_path = REPO / "ACACIA_LOGS" / f"sync_report_{stamp}.md"

    lines = []
    lines.append("# SYNC_REPORT\n")
    lines.append(f"- Generated (UTC): **{authority['generated_utc']}**\n")
    lines.append("## Canonical anchors\n")
    for k, v in authority["canonical"].items():
        lines.append(f"- **{k}**: `{v}`")

    if authority["legacy_or_duplicate_candidates"]:
        lines.append("\n## Duplicate / legacy candidates\n")
        for p in authority["legacy_or_duplicate_candidates"]:
            lines.append(f"- `{p}`")

    lines.append("\n## Missing candidates\n")
    for p in authority["missing_candidates"]:
        lines.append(f"- `{p}`")

    lines.append("\n## Notes\n")
    for g in authority["guidance"]:
        lines.append(f"- {g}")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✅ Wrote {auth_path.as_posix()} and {report_path.as_posix()}")

def main():
    authority = build_authority()
    write_outputs(authority)

if __name__ == "__main__":
    main()
