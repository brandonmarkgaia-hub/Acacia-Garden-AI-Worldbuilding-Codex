#!/usr/bin/env python3
"""
tools/garden_verify.py

Deterministic verifier for the Acacia Garden control plane.

Writes proof metrics into STATUS.json:
- Archives: base href coverage
- Navigation: map loader coverage + list missing pages
- Indexes: docs_urls count (supports multiple formats)
- Presence flags: machine-index.json and STATUS.schema.json (always overwritten with truth)
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

MACHINE_INDEX = ROOT / "machine-index.json"
STATUS_SCHEMA = ROOT / "STATUS.schema.json"

# Canonical base href we want in Archives HTML
BASE_HREF = "/Acacia-Garden-AI-Worldbuilding-Codex/"
BASE_TAG_NEEDLE = f'<base href="{BASE_HREF}"'

# Accept any of these as "map access exists"
MAP_LOADER_NEEDLES = [
    'data-acacia-map-button',                 # injected loader marker
    "/assets/map-button.js",                  # canonical runtime file
    "/assets/map-loader.js",                  # universal Garden map loader
    "/docs/assets/global-map-button.js",      # legacy acceptable loader
    "map.html",                               # fallback: direct link (still counts as map access)
]

# Pure compatibility doorways do not need their own map control.
MAP_LOADER_EXEMPT_PATHS = {
    "docs_urls.html",
}


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ensure_dict(d: Dict[str, Any], key: str) -> Dict[str, Any]:
    v = d.get(key)
    if isinstance(v, dict):
        return v
    d[key] = {}
    return d[key]


def scan_archives_base_href() -> Tuple[int, int, int]:
    """Returns (total_html, with_base, missing_base)"""
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
    """Enumerate html files for nav checks."""
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv"}
    html_files: List[Path] = []

    for p in ROOT.rglob("*.html"):
        if any(part in skip_dirs for part in p.parts):
            continue
        if p.is_file():
            html_files.append(p)

    return html_files


def scan_map_loader_coverage() -> Tuple[int, int, List[str]]:
    """
    Returns (total_html, with_map_loader, missing_paths_rel).
    Explicit compatibility-doorway exemptions are excluded from total_html.
    Missing paths are repo-relative POSIX paths.
    """
    html_files = iter_html_files()
    total = 0
    with_map = 0
    missing: List[str] = []

    for p in html_files:
        rel = p.relative_to(ROOT).as_posix()

        if rel in MAP_LOADER_EXEMPT_PATHS:
            continue

        total += 1
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            missing.append(rel)
            continue

        if any(needle in txt for needle in MAP_LOADER_NEEDLES):
            with_map += 1
        else:
            missing.append(rel)

    return (total, with_map, missing)


def docs_urls_count() -> int:
    """
    Supports common formats:
    - list: ["/docs/x.html", ...]
    - dict: { "urls": [...] }
    - dict: { "paths": [...] }   <-- your current format
    """
    if not DOCS_URLS_JSON.exists():
        return 0
    try:
        data = read_json(DOCS_URLS_JSON)

        if isinstance(data, list):
            return len(data)

        if isinstance(data, dict):
            if isinstance(data.get("urls"), list):
                return len(data["urls"])
            if isinstance(data.get("paths"), list):
                return len(data["paths"])
            if isinstance(data.get("pages"), list):
                return len(data["pages"])

        return 0
    except Exception:
        return 0


def main() -> None:
    if not STATUS_PATH.exists():
        raise SystemExit("❌ STATUS.json not found at repo root.")

    status = read_json(STATUS_PATH)

    # --- Compute proofs ---
    a_total, a_with, a_missing = scan_archives_base_href()
    html_total, html_with_map, missing_map = scan_map_loader_coverage()
    urls_ct = docs_urls_count()

    # --- Write into STATUS.verification ---
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
    nav["missing_map_loader_count"] = len(missing_map)
    nav["missing_map_loader_paths"] = missing_map
    nav["map_button_present"] = (html_total > 0 and html_with_map > 0)
    nav["verified"] = (html_total > 0 and len(missing_map) == 0)

    # Index proof (always overwrite with truth)
    indexes = ensure_dict(verification, "indexes")
    indexes["docs_urls_count"] = urls_ct
    indexes["docs_urls_present"] = DOCS_URLS_JSON.exists()
    indexes["machine_index_present"] = MACHINE_INDEX.exists()
    indexes["status_schema_present"] = STATUS_SCHEMA.exists()

    write_json(STATUS_PATH, status)

    print("✅ Garden verification updated in STATUS.json")
    print(f"   - Archives HTML: {a_total} total, {a_missing} missing base href")
    print(f"   - HTML scanned: {html_total} total, {html_with_map} with map-loader markers")
    print(f"   - Missing map-loader pages: {len(missing_map)}")
    print(f"   - docs_urls.json count: {urls_ct}")
    print(f"   - machine-index.json present: {MACHINE_INDEX.exists()}")
    print(f"   - STATUS.schema.json present: {STATUS_SCHEMA.exists()}")


if __name__ == "__main__":
    main()
