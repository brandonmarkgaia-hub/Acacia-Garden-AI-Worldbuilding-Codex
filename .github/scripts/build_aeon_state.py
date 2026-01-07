#!/usr/bin/env python3
"""
build_aeon_state.py

Builds a single, dashboard-friendly JSON snapshot of the Garden
for the Aeon Console.

Inputs (must already exist in repo root):
  - STATUS.json
  - machine-index.json

Output (written to STATE/):
  - aeon_state.json
"""

from __future__ import annotations

import json
import datetime as _dt
from pathlib import Path

# .github/scripts -> .github -> repo root
ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "STATE"


def _utc_now_iso() -> str:
    return _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _count_md(prefixes: list[str]) -> int:
    """
    Count *.md files under one or more folder prefixes (relative to ROOT).
    """
    total = 0
    for prefix in prefixes:
        folder = ROOT / prefix
        if not folder.exists():
            continue
        for _ in folder.rglob("*.md"):
            total += 1
    return total


def _count_archives() -> int:
    # Archive pages are static HTML under docs/Archives/
    folder = ROOT / "docs" / "Archives"
    if not folder.exists():
        return 0
    return sum(1 for _ in folder.rglob("*.html"))


def build_counts() -> dict:
    """
    Derive high-level Garden counts directly from the filesystem.
    """

    # Any folder with "Chambers" in its name is a chamber source
    chambers_prefixes: list[str] = []
    for path in ROOT.rglob("*Chambers*"):
        if path.is_dir():
            chambers_prefixes.append(str(path.relative_to(ROOT)))

    counts = {
        "chambers": _count_md(chambers_prefixes),
        "blooms": _count_md(["Blooms", "docs/Blooms"]),
        "echoes": _count_md(["docs/Echoes"]),
        "vaults": _count_md(["docs/Vault", "docs/Vaults"]),
        "laws": _count_md(["Laws", "docs/Laws"]),
        "orchards": _count_md(["Orchards", "docs/Orchards"]),
        "cycles": _count_md(["cycles", "docs/Cycles"]),
        "novellas": _count_md(["docs/Novellas"]),
        "archives": _count_archives(),
    }
    return counts


def build_echo_growth(machine_index: dict | None):
    """
    Build a compact "echo_growth" list from machine-index.json.
    Returns (echo_growth_list, echo_count, legacy_meta)
    """
    if not machine_index:
        return [], 0, {}

    entries = machine_index.get("entries", [])
    echo_entries = [
        e
        for e in entries
        if isinstance(e, dict)
        and str(e.get("path", "")).startswith("docs/Echoes/")
    ]

    def sort_key(e: dict):
        return str(e.get("timestamp", ""))

    echo_entries_sorted = sorted(echo_entries, key=sort_key, reverse=True)

    echo_growth = [
        {
            "file": e.get("path"),
            "timestamp": e.get("timestamp"),
            "title": e.get("title"),
            "tags": e.get("tags", []),
        }
        for e in echo_entries_sorted[:120]
    ]

    echo_count = len(echo_entries)
    legacy_meta = {
        "generated_at": machine_index.get("generated_at"),
        "meta": machine_index.get("meta", {}),
        "total_entries": machine_index.get("counts", {}).get("total", len(entries)),
    }
    return echo_growth, echo_count, legacy_meta


def main() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    status = _read_json(ROOT / "STATUS.json")
    machine_index = _read_json(ROOT / "machine-index.json")

    counts = build_counts()
    echo_growth, echo_count, machine_legacy = build_echo_growth(machine_index)

    payload = {
        "generated_utc": _utc_now_iso(),
        "meta": {
            "keeper": "HKX277206",
            "source": "build_aeon_state.py",
            "status_source": "STATUS.json" if status else None,
            "machine_index_source": "machine-index.json" if machine_index else None,
        },
        "counts": counts,
        "echo_growth": echo_growth,
        "echo_count": echo_count,
        "legacy": machine_legacy,
    }

    out_path = STATE_DIR / "aeon_state.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[aeon-state] wrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
