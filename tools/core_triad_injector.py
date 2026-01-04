#!/usr/bin/env python3
"""
core_triad_injector.py

Purpose
- Create *injected* (merged) versions of the Garden's core triad JSON files
  WITHOUT overwriting the originals.

Outputs (created/updated)
- STATE/status.inject.json
- STATE/aeon_heartbeat.inject.json
- STATE/machine_index.inject.json
- STATE/garden_scan_report.inject.json
- ACACIA_LOGS/core_triad_injection_<YYYYMMDD_HHMMSS>.md

Design
- Non-destructive: originals are read-only inputs.
- Merge strategy: preserve existing root keys; inject under safe namespaces:
    meta.injection and inject.core_triad
- Works with legacy filenames/casing via candidate lists.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO = Path(".").resolve()

STATUS_CANDIDATES = [
    "STATUS.json",
    "status.json",
    "STATE/STATUS_v2.json",
]
HEARTBEAT_CANDIDATES = [
    "logs/aeon_heartbeat.json",
    "aeon_heartbeat.json",
    "AEON_HEARTBEAT.json",
]
MACHINE_INDEX_CANDIDATES = [
    "machine-index.json",
    "machine_index.json",
    "MACHINE-INDEX.json",
    "tools/machine-index.json",
    "tools/machine_index.json",
]
SCAN_REPORT_CANDIDATES = [
    "garden_scan_report.json",
    "GARDEN_SCAN_REPORT.json",
    "tools/GARDEN_SCAN_REPORT.json",
    "tools/garden_scan_report.json",
]

OUT_MAP = {
    "status": Path("STATE/status.inject.json"),
    "heartbeat": Path("STATE/aeon_heartbeat.inject.json"),
    "machine_index": Path("STATE/machine_index.inject.json"),
    "scan_report": Path("STATE/garden_scan_report.inject.json"),
}

LOG_DIR = Path("ACACIA_LOGS")

KEEPER_SEAL = "HKX277206"


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _find_first(candidates: List[str]) -> Optional[Path]:
    for c in candidates:
        p = REPO / c
        if p.exists() and p.is_file():
            return p
    return None


def _deep_merge_keep_left(base: Dict[str, Any], inject: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge inject into base but NEVER delete base keys.
    - If both values are dicts: recurse.
    - Otherwise: inject overwrites that specific leaf.
    """
    out = dict(base)
    for k, v in inject.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge_keep_left(out[k], v)
        else:
            out[k] = v
    return out


def _inject_payload(now_iso: str) -> Dict[str, Any]:
    return {
        "meta": {
            "injection": {
                "generated_utc": now_iso,
                "keeper": KEEPER_SEAL,
                "mode": "inject-no-overwrite",
                "note": "Core triad injection artifact. Originals left untouched."
            }
        },
        "inject": {
            "core_triad": {
                "generated_utc": now_iso,
                "keeper": KEEPER_SEAL,
                "phase": "2026",
                "health": "STABLE",
            }
        }
    }


@dataclass
class InputPick:
    label: str
    chosen: Optional[Path]
    tried: List[str]


def pick_inputs() -> Dict[str, InputPick]:
    return {
        "status": InputPick("status", _find_first(STATUS_CANDIDATES), STATUS_CANDIDATES),
        "heartbeat": InputPick("heartbeat", _find_first(HEARTBEAT_CANDIDATES), HEARTBEAT_CANDIDATES),
        "machine_index": InputPick("machine_index", _find_first(MACHINE_INDEX_CANDIDATES), MACHINE_INDEX_CANDIDATES),
        "scan_report": InputPick("scan_report", _find_first(SCAN_REPORT_CANDIDATES), SCAN_REPORT_CANDIDATES),
    }


def write_outputs(picks: Dict[str, InputPick]) -> Dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = _inject_payload(now_iso)

    state_dir = REPO / "STATE"
    state_dir.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    summary: Dict[str, Any] = {"generated_utc": now_iso, "keeper": KEEPER_SEAL, "inputs": {}, "outputs": {}}

    for key, pick in picks.items():
        out_rel = OUT_MAP[key]
        out_path = REPO / out_rel

        base_obj: Dict[str, Any] = {}
        if pick.chosen:
            read = _read_json(pick.chosen)
            if isinstance(read, dict):
                base_obj = read

        merged = _deep_merge_keep_left(base_obj, payload)

        # Also stamp a convenient top-level hint without clobbering existing
        if "generated_at" not in merged:
            merged["generated_at"] = now_iso

        out_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        summary["inputs"][key] = {
            "chosen": pick.chosen.as_posix() if pick.chosen else None,
            "tried": pick.tried,
            "found": bool(pick.chosen),
        }
        summary["outputs"][key] = out_rel.as_posix()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    md = []
    md.append("# CORE_TRIAD_INJECTION\n")
    md.append(f"- Generated (UTC): **{now_iso}**")
    md.append(f"- Keeper: **{KEEPER_SEAL}**\n")
    md.append("## Inputs\n")
    for k, v in summary["inputs"].items():
        md.append(f"- **{k}**: `{v['chosen']}`" if v["chosen"] else f"- **{k}**: ❌ not found (tried: {', '.join(v['tried'])})")
    md.append("\n## Outputs\n")
    for k, v in summary["outputs"].items():
        md.append(f"- **{k}**: `{v}`")
    (REPO / LOG_DIR / f"core_triad_injection_{stamp}.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # Write machine-readable summary too (useful later)
    (REPO / "STATE" / "core_triad_injection.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return summary


def main():
    picks = pick_inputs()
    summary = write_outputs(picks)
    print("✅ Core triad injected (non-destructive).")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
