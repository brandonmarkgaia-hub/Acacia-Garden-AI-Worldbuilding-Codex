#!/usr/bin/env python3
"""
tools/garden_verify.py

Deterministic verifier for the Acacia Garden control plane.

Writes proof metrics into STATUS.json:
- Archives: base href coverage
- Navigation: map button loader coverage
- Indexes: docs_urls count (from docs/docs_urls.json)
- last_verified_utc stamp

No external deps.
"""

from __future__ import annotations

import json
import datetime as dt
from pathlib import Path
from typing import Dict, Any, Tuple, List


ROOT = Path(__file__).resolve().parent.parent

STATUS_PATH = ROOT / "STATUS.json"
ARCHIVES_DIR = ROOT / "docs" / "Archives"
DOCS_URLS_JSON = ROOT / "docs" / "docs_urls.json"

# Canonical base href we want in Archives HTML
BASE_HREF = "/Acacia-Garden-AI-Worldbuilding-Codex/"
BASE_TAG_NEEDLE = f'<base href="{BASE_HREF}"'

# Accept either of your map-loader systems as "map button present"
MAP_LOADER_NEEDLES = [
    'data-acacia-map-button',                   # injected loader marker
    "/assets/map-button.js",                    # canonical runtime button file
    "/docs/assets/global-map-button.js",        # legacy global loader (still acceptable)
]


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def scan_archives_base_href() -> Tuple[int, int, int]:
    """
    Returns (total_html, with_base, missing_base)
    """
    if not ARCHIVES_DIR.exists():
        return (0, 0, 0)

    total = 0
    with_base = 0

    for p in ARCHIVES_DIR.rglob("*.html"):
        if not p.is_file():
            continue
        total += 1
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if BASE_TAG_NEEDLE in txt:
            with_base += 1

    missing = max(0, total - with_base)
    return (total, with_base, missing)


def iter_html_files() -> List[Path]:
    """
    Enumerate html files for nav checks.
    Avoid scanning huge irrelevant dirs if present.
    """
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv"}
    html_files: List[Path] = []

    # scan repo for .html files
    for p in ROOT.rglob("*.html"):
        # skip if any parent dir is in skip set
        if any(part in skip_dirs for part in p.parts):
            continue
        if p.is_file():
            html_files.append(p)

    return html_files


def scan_map_loader_coverage() -> Tuple[int, int]:
    """
    Returns (total_html, with_map_loader)
    We consider the map accessible if page includes one of known loader markers.
    """
    html_files = iter_html_files()
    total = 0
    with_map = 0

    for p in html_files:
        total += 1
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if any(needle in txt for needle in MAP_LOADER_NEEDLES):
            with_map += 1

    return (total, with_map)


def docs_urls_count() -> int:
    if not DOCS_URLS_JSON.exists():
        return 0
    try:
        data = read_json(DOCS_URLS_JSON)
        if isinstance(data, list):
            return len(data)
        if isinstance(data, dict) and "urls" in data and isinstance(data["urls"], list):
            return len(data["urls"])
        return 0
    except Exception:
        return 0


def ensure_dict(d: Dict[str, Any], key: str) -> Dict[str, Any]:
    v = d.get(key)
    if isinstance(v, dict):
        return v
    d[key] = {}
    return d[key]


def main() -> None:
    if not STATUS_PATH.exists():
        raise SystemExit("❌ STATUS.json not found at repo root.")

    status = read_json(STATUS_PATH)

    # Compute proofs
    a_total, a_with, a_missing = scan_archives_base_href()
    html_total, html_with_map = scan_map_loader_coverage()
    urls_ct = docs_urls_count()

    # Write into STATUS.verification (create if missing)
    verification = ensure_dict(status, "verification")
    verification["last_verified_utc"] = utc_now_iso()

    # Archives proof
    archives = ensure_dict(verification, "archives")
    archives["total_html"] = a_total
    archives["with_base_href"] = a_with
    archives["missing_base_href"] = a_missing
    archives["verified"] = (a_total > 0 and a_missing == 0)

    # Navigation proof
    nav = ensure_dict(verification, "navigation")
    nav["total_html_scanned"] = html_total
    nav["with_map_loader"] = html_with_map
    nav["map_button_present"] = (html_total > 0 and html_with_map > 0)
    nav["verified"] = (html_total > 0 and html_with_map == html_total)

    # Index proof
    indexes = ensure_dict(verification, "indexes")
    indexes["docs_urls_count"] = urls_ct
    indexes["docs_urls_present"] = DOCS_URLS_JSON.exists()

    # Keep existing flags if present; otherwise set conservative defaults
    if "machine_index_present" not in indexes:
        indexes["machine_index_present"] = (ROOT / "machine-index.json").exists()
    if "status_schema_present" not in indexes:
        indexes["status_schema_present"] = (ROOT / "STATUS.schema.json").exists()

    write_json(STATUS_PATH, status)

    print("✅ Garden verification updated in STATUS.json")
    print(f"   - Archives HTML: {a_total} total, {a_missing} missing base href")
    print(f"   - HTML scanned: {html_total} total, {html_with_map} with map-loader markers")
    print(f"   - docs_urls.json count: {urls_ct}")


if __name__ == "__main__":
    main()
