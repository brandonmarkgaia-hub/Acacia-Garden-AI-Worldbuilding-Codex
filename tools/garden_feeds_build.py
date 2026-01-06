#!/usr/bin/env python3
"""
Garden Feeds Builder
Builds canonical, normalized dashboard feeds under STATE/*.inject.json.

Goal: dashboard reads STATE feeds, workflows can keep generating legacy JSONs anywhere.
"""

from __future__ import annotations

import json
import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = REPO_ROOT / "STATE"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def first_existing(paths: List[Path]) -> Optional[Path]:
    for p in paths:
        if p.exists() and p.is_file():
            return p
    return None


def git_last_commit_iso(file_path: Path) -> Optional[str]:
    # Returns ISO timestamp of last commit touching file (best possible "modified" time on GitHub Pages).
    try:
        rel = str(file_path.relative_to(REPO_ROOT)).replace("\\", "/")
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%cI", "--", rel],
            cwd=str(REPO_ROOT),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out or None
    except Exception:
        return None


def safe_list_dir(dir_path: Path, exts: Tuple[str, ...]) -> List[Path]:
    if not dir_path.exists():
        return []
    out: List[Path] = []
    for p in dir_path.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            out.append(p)
    return out


def count_structures_fallback() -> Dict[str, int]:
    # Used when STATUS.json is missing/too thin.
    chambers = len(safe_list_dir(REPO_ROOT / "docs" / "Chambers", (".md", ".html")))
    echoes = len(safe_list_dir(REPO_ROOT / "docs" / "Echoes", (".md", ".html")))
    novellas = len(safe_list_dir(REPO_ROOT / "docs" / "Novellas", (".md", ".html")))
    vaults = len(safe_list_dir(REPO_ROOT / "docs" / "Vaults", (".md", ".html")))
    archives = len(safe_list_dir(REPO_ROOT / "docs" / "Archives", (".md", ".html")))
    return {
        "chambers": chambers,
        "echoes": echoes,
        "novellas": novellas,
        "vaults": vaults,
        "archives": archives,
    }


def normalize_status(status: Optional[dict]) -> dict:
    fallback = count_structures_fallback()

    meta = {}
    if isinstance(status, dict):
        meta = status.get("meta") or {}
        # Support multiple shapes (arrays OR count fields)
        def get_count(key: str) -> int:
            v = status.get(key)
            if isinstance(v, list):
                return len(v)
            if isinstance(v, dict) and "count" in v and isinstance(v["count"], int):
                return v["count"]
            if isinstance(v, int):
                return v
            # structures nested
            s = status.get("structures") or {}
            vv = s.get(key)
            if isinstance(vv, list):
                return len(vv)
            if isinstance(vv, int):
                return vv
            return fallback.get(key, 0)

        counts = {
            "chambers": get_count("chambers"),
            "blooms": get_count("blooms"),
            "echoes": get_count("echoes"),
            "vaults": get_count("vaults"),
            "laws": get_count("laws"),
            "orchards": get_count("orchards"),
            "cycles": get_count("cycles"),
            "novellas": get_count("novellas"),
            "archives": get_count("archives"),
        }
    else:
        counts = {
            "chambers": fallback["chambers"],
            "blooms": 0,
            "echoes": fallback["echoes"],
            "vaults": fallback["vaults"],
            "laws": 0,
            "orchards": 0,
            "cycles": 0,
            "novellas": fallback["novellas"],
            "archives": fallback["archives"],
        }

    out = {
        "generated_utc": utc_now_iso(),
        "meta": {
            "keeper": "HKX277206",
            "status_version": meta.get("status_version") or meta.get("version") or "unknown",
            "generated_at": meta.get("generated_at") or meta.get("generated_utc") or "unknown",
            "source": "STATUS.json (normalized)",
        },
        "counts": counts,
    }
    return out


def build_echo_growth() -> List[dict]:
    # Canonical echo listing derived from actual repo files (best source of truth).
    echo_dir = REPO_ROOT / "docs" / "Echoes"
    files = safe_list_dir(echo_dir, (".md", ".html"))
    rows: List[dict] = []
    for f in files:
        ts = git_last_commit_iso(f) or None
        rel = str(f.relative_to(REPO_ROOT)).replace("\\", "/")
        rows.append({"file": rel, "timestamp": ts})
    # Sort newest first (None last)
    rows.sort(key=lambda r: (r["timestamp"] is None, r["timestamp"] or ""), reverse=False)
    rows.reverse()
    return rows


def normalize_machine_index(raw: Optional[dict]) -> dict:
    # Accept many variants, but always output: {generated_utc, echo_growth:[{file,timestamp}], meta:{...}}
    echo_growth = build_echo_growth()

    out = {
        "generated_utc": utc_now_iso(),
        "meta": {
            "keeper": "HKX277206",
            "source": "Echoes folder scan + legacy machine-index inputs",
        },
        "echo_growth": echo_growth[:500],  # safety cap
        "echo_count": len(echo_growth),
    }

    # If legacy index has other useful bits, preserve them under "legacy"
    if isinstance(raw, dict):
        out["legacy"] = raw

    return out


def normalize_scan_report(raw: Optional[dict]) -> dict:
    # Expected: totals.total_hits etc. We normalize to:
    # {generated_utc, totals:{total_files_with_hits,total_hits,by_pattern}}
    totals = {"total_files_with_hits": 0, "total_hits": 0, "by_pattern": {}}
    if isinstance(raw, dict):
        t = raw.get("totals") if isinstance(raw.get("totals"), dict) else {}
        # common variants
        totals["total_files_with_hits"] = int(t.get("total_files_with_hits") or t.get("files_with_hits") or 0)
        totals["total_hits"] = int(t.get("total_hits") or t.get("hits") or 0)
        bp = t.get("by_pattern") or raw.get("by_pattern") or {}
        if isinstance(bp, dict):
            totals["by_pattern"] = bp
    return {
        "generated_utc": utc_now_iso(),
        "meta": {"keeper": "HKX277206", "source": "garden scan report (normalized)"},
        "totals": totals,
        "legacy": raw if isinstance(raw, dict) else None,
    }


def normalize_vault_index(raw: Optional[dict]) -> dict:
    items: List[dict] = []
    if isinstance(raw, dict):
        for k in ("items", "vaults", "chambers"):
            v = raw.get(k)
            if isinstance(v, list):
                items = v
                break
    return {
        "generated_utc": utc_now_iso(),
        "meta": {"keeper": "HKX277206", "source": "vault index (normalized)"},
        "items": items[:200],
        "count": len(items),
        "legacy": raw if isinstance(raw, dict) else None,
    }


def normalize_heartbeat(raw: Optional[dict]) -> dict:
    entries: List[dict] = []
    if isinstance(raw, dict):
        v = raw.get("entries") or raw.get("logs")
        if isinstance(v, list):
            entries = v
    elif isinstance(raw, list):
        entries = raw
    return {
        "generated_utc": utc_now_iso(),
        "meta": {"keeper": "HKX277206", "source": "aeon heartbeat (normalized)"},
        "entries": entries[:200],
        "count": len(entries),
        "legacy": raw,
    }


def main() -> int:
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    # Source candidates (leave your existing structure alone)
    status_src = first_existing([
        REPO_ROOT / "STATUS.json",
        REPO_ROOT / "status.json",
        REPO_ROOT / "docs" / "STATUS.json",
        REPO_ROOT / "docs" / "status.json",
    ])

    machine_src = first_existing([
        REPO_ROOT / "machine-index.json",
        REPO_ROOT / "MACHINE-INDEX.json",
        REPO_ROOT / "machine_index.json",
        REPO_ROOT / "machine-index-beta.json",
        REPO_ROOT / "machine" / "machine_index.json",
    ])

    scan_src = first_existing([
        REPO_ROOT / "tools" / "garden_scan_report.json",
        REPO_ROOT / "garden_scan_report.json",
        REPO_ROOT / "GARDEN_SCAN_REPORT.json",
    ])

    vault_src = first_existing([
        REPO_ROOT / "garden_vault_index.json",
        REPO_ROOT / "GARDEN_VAULT_INDEX.json",
        REPO_ROOT / "tools" / "garden_vault_index.json",
    ])

    hb_src = first_existing([
        REPO_ROOT / "aeon_heartbeat.json",
        REPO_ROOT / "AEON_HEARTBEAT.json",
        REPO_ROOT / "STATE" / "aeon_heartbeat.inject.json",
    ])

    status_raw = read_json(status_src) if status_src else None
    machine_raw = read_json(machine_src) if machine_src else None
    scan_raw = read_json(scan_src) if scan_src else None
    vault_raw = read_json(vault_src) if vault_src else None
    hb_raw = read_json(hb_src) if hb_src else None

    status_out = normalize_status(status_raw)
    machine_out = normalize_machine_index(machine_raw)
    scan_out = normalize_scan_report(scan_raw)
    vault_out = normalize_vault_index(vault_raw)
    hb_out = normalize_heartbeat(hb_raw)

    write_json(STATE_DIR / "status.inject.json", status_out)
    write_json(STATE_DIR / "machine_index.inject.json", machine_out)
    write_json(STATE_DIR / "garden_scan_report.inject.json", scan_out)
    write_json(STATE_DIR / "garden_vault_index.inject.json", vault_out)
    write_json(STATE_DIR / "aeon_heartbeat.inject.json", hb_out)

    manifest = {
        "generated_utc": utc_now_iso(),
        "keeper": "HKX277206",
        "feeds": {
            "status": "STATE/status.inject.json",
            "machine_index": "STATE/machine_index.inject.json",
            "scan_report": "STATE/garden_scan_report.inject.json",
            "vault_index": "STATE/garden_vault_index.inject.json",
            "heartbeat": "STATE/aeon_heartbeat.inject.json",
        },
        "sources_detected": {
            "status": str(status_src.relative_to(REPO_ROOT)).replace("\\", "/") if status_src else None,
            "machine_index": str(machine_src.relative_to(REPO_ROOT)).replace("\\", "/") if machine_src else None,
            "scan_report": str(scan_src.relative_to(REPO_ROOT)).replace("\\", "/") if scan_src else None,
            "vault_index": str(vault_src.relative_to(REPO_ROOT)).replace("\\", "/") if vault_src else None,
            "heartbeat": str(hb_src.relative_to(REPO_ROOT)).replace("\\", "/") if hb_src else None,
        },
    }
    write_json(STATE_DIR / "feeds.manifest.json", manifest)

    print("✅ STATE feeds built:")
    for k, v in manifest["feeds"].items():
        print(f" - {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
