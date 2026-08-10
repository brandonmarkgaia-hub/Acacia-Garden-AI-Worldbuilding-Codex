#!/usr/bin/env python3
"""
tools/rcs.py

RITUAL OF CADENCE SYNTHESIS (RCS) — proposal-only state integration.
Inputs:
  - Latest EVOLUTION/Desire_YYYYMMDD.md (required)
  - Optional EVOLUTION/Desire_YYYYMMDD.json (preferred if present)
  - STATUS.json (optional, used as baseline)
Outputs:
  - STATE/STATUS_vYYYYMMDD_HHMM.json (proposal)
  - STATE/cadence_anchors.json (append-only log)
  - (optional) Append a short entry to GOLDEN_NULL_INDEX.md

This tool does not overwrite STATUS.json automatically.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(".").resolve()

def find_latest_desire():
    evo = REPO / "EVOLUTION"
    if not evo.exists():
        return None
    desires = sorted(evo.glob("Desire_*.md"))
    if not desires:
        return None
    return desires[-1]

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def safe_read_text(path: Path, limit: int = 100000):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""

def extract_desire_title(md_text: str) -> str:
    # first markdown header or first non-empty line
    for line in md_text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            return s.lstrip("#").strip()
        return s[:120]
    return "Untitled Desire"

def build_proposal(latest_md: Path):
    now = datetime.now(timezone.utc)
    ts_version = now.strftime("%Y%m%d_%H%M")
    md_text = safe_read_text(latest_md, limit=200000)
    title = extract_desire_title(md_text)

    base_state = load_json(REPO / "STATUS.json") or {}
    base_state.setdefault("schema_version", "unknown")
    base_state.setdefault("active_evolution_anchor", None)

    # optional sidecar json
    sidecar = latest_md.with_suffix(".json")
    sidecar_data = load_json(sidecar) if sidecar.exists() else None

    proposal = dict(base_state)
    proposal["schema_version"] = ts_version
    proposal["active_evolution_anchor"] = latest_md.name.replace(".md", "")
    proposal["rcs"] = {
        "generated_utc": now.isoformat(),
        "source_desire_md": latest_md.as_posix().replace(str(REPO)+"/",""),
        "source_desire_title": title,
        "sidecar_json_present": bool(sidecar_data),
    }

    # minimal, safe merging if sidecar contains a dict
    if isinstance(sidecar_data, dict):
        # only merge into a namespaced section to avoid breaking existing consumers
        proposal["rcs"]["sidecar"] = sidecar_data

    return ts_version, proposal

def append_cadence_anchor(ts_version: str, desire_name: str):
    anchors_path = REPO / "STATE" / "cadence_anchors.json"
    anchors_path.parent.mkdir(parents=True, exist_ok=True)
    anchors = load_json(anchors_path) or {"anchors": []}

    anchors["anchors"].append({
        "version": ts_version,
        "desire": desire_name,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    })

    anchors_path.write_text(json.dumps(anchors, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return anchors_path

def append_golden_null(ts_version: str, desire_name: str):
    gni = REPO / "GOLDEN_NULL_INDEX.md"
    if not gni.exists():
        return None
    line = f"- CADENCE_SYNTHESIS_PROPOSAL `{ts_version}` -> `{desire_name}` ({datetime.now(timezone.utc).isoformat()})\n"
    try:
        with gni.open("a", encoding="utf-8") as f:
            f.write(line)
        return gni
    except Exception:
        return None

def main():
    latest = find_latest_desire()
    if not latest:
        raise SystemExit("No EVOLUTION/Desire_*.md found. Nothing to synthesize.")

    ts_version, proposal = build_proposal(latest)
    out_path = REPO / "STATE" / f"STATUS_v{ts_version}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(proposal, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    anchors_path = append_cadence_anchor(ts_version, latest.name.replace(".md",""))
    gni_path = append_golden_null(ts_version, latest.name.replace(".md",""))

    print(f"✅ Proposed state: {out_path.as_posix()}")
    print(f"✅ Cadence anchors: {anchors_path.as_posix()}")
    if gni_path:
        print(f"✅ Golden Null Index updated: {gni_path.as_posix()}")

if __name__ == "__main__":
    main()
