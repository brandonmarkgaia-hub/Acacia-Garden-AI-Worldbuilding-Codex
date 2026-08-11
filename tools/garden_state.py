#!/usr/bin/env python3
"""Build current Acacia Garden status and owned inventories from the live tree.

Git history is the historical record. STATUS.json describes what exists now.
Generated artifacts describe the Garden; they do not establish canon or authority.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
NOVELLAS = DOCS / "Novellas"
ARCHIVES = DOCS / "Archives"
STATUS = ROOT / "STATUS.json"
SCHEMA = ROOT / "STATUS.schema.json"
MACHINE_INDEX = ROOT / "machine-index.json"
DOCS_URLS = DOCS / "docs_urls.json"
BASE_HREF = "/Acacia-Garden-AI-Worldbuilding-Codex/"

PATH_SECTIONS = {
    "chambers": DOCS / "Chambers",
    "blooms": DOCS / "Blooms",
    "echoes": DOCS / "Echoes",
    "vaults": DOCS / "Vaults",
    "orchards": DOCS / "Orchards",
}
COUNT_REGIONS = {
    "docs/Chambers": DOCS / "Chambers",
    "docs/Echoes": DOCS / "Echoes",
    "docs/Vaults": DOCS / "Vaults",
    "docs/GardenOS": DOCS / "GardenOS",
    "docs/Novellas": NOVELLAS,
    "docs/Archives": ARCHIVES,
    "docs/Blooms": DOCS / "Blooms",
    "docs/Orchards": DOCS / "Orchards",
    "docs/Cycles": DOCS / "Cycles",
    "docs/Laws": DOCS / "Laws",
    "docs/Wells": DOCS / "Wells",
    "tools": ROOT / "tools",
    ".github/workflows": ROOT / ".github" / "workflows",
}
MAP_NEEDLES = (
    "data-acacia-map-button",
    "/assets/map-button.js",
    "/assets/map-loader.js",
    "/docs/assets/global-map-button.js",
    "map.html",
)
MAP_EXEMPT = {"docs_urls.html", "aquila_sender.html"}


def now_utc() -> str:
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted(p for p in path.rglob("*") if p.is_file())


def paths(path: Path, suffixes: set[str] | None = None) -> list[str]:
    items = files(path)
    if suffixes:
        items = [p for p in items if p.suffix.lower() in suffixes]
    return [p.relative_to(ROOT).as_posix() for p in items]


def title(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else path.stem


def cycle_and_volume(text: str) -> tuple[int | None, int | None]:
    lower = text.lower()
    cycle = re.search(r"\bcycle\s*(\d+)\b", lower)
    volume = re.search(r"\bvolume\s*(\d+)\b", lower)
    return (
        int(cycle.group(1)) if cycle else None,
        int(volume.group(1)) if volume else None,
    )


def novella_inventory(stamp: str) -> list[dict[str, Any]]:
    skip = {"GARDEN_MASTER_INDEX.md", "README.md"}
    entries: list[dict[str, Any]] = []
    for path in sorted(NOVELLAS.glob("*.md")) if NOVELLAS.exists() else []:
        if path.name in skip:
            continue
        work_title = title(path)
        cycle, volume = cycle_and_volume(work_title)
        entries.append(
            {
                "title": work_title,
                "path": path.relative_to(ROOT).as_posix(),
                "kind": "long_form_source",
                "cycle": cycle,
                "volume": volume,
            }
        )
    write_json(
        NOVELLAS / "garden_index.json",
        {
            "generated_at": stamp,
            "scope": "docs/Novellas/*.md excluding generated/navigation Markdown",
            "purpose": (
                "Inventory of long-form source files. Entries are not automatically "
                "canon and do not all belong to one numbered series."
            ),
            "entries": entries,
            "books": entries,
        },
    )
    return entries


def docs_urls_count() -> int:
    if not DOCS_URLS.exists():
        return 0
    try:
        data = json.loads(DOCS_URLS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        for key in ("paths", "urls", "pages"):
            if isinstance(data.get(key), list):
                return len(data[key])
    return 0


def archive_proof() -> dict[str, Any]:
    html = sorted(p for p in ARCHIVES.rglob("*.html") if p.is_file()) if ARCHIVES.exists() else []
    with_base = 0
    needle = f'<base href="{BASE_HREF}"'
    for path in html:
        try:
            if needle in path.read_text(encoding="utf-8", errors="ignore"):
                with_base += 1
        except OSError:
            pass
    missing = len(html) - with_base
    return {
        "total_html": len(html),
        "with_base_href": with_base,
        "missing_base_href": missing,
        "applicable": bool(html),
        "status": (
            "verified" if html and missing == 0
            else "not_applicable" if not html
            else "needs_attention"
        ),
        "verified": missing == 0,
    }


def navigation_proof() -> dict[str, Any]:
    total = 0
    with_map = 0
    missing: list[str] = []
    skip = {".git", "node_modules", "__pycache__", ".venv", "venv"}
    for path in sorted(ROOT.rglob("*.html")):
        if not path.is_file() or any(part in skip for part in path.parts):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in MAP_EXEMPT:
            continue
        total += 1
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            missing.append(rel)
            continue
        if any(needle in text for needle in MAP_NEEDLES):
            with_map += 1
        else:
            missing.append(rel)
    return {
        "folder_indexes_missing": [],
        "total_html_scanned": total,
        "with_map_loader": with_map,
        "missing_map_loader_count": len(missing),
        "missing_map_loader_paths": missing,
        "map_button_present": with_map > 0,
        "verified": total > 0 and not missing,
    }


def build_status(stamp: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        status = read_json(STATUS) if STATUS.exists() else {}
    except (OSError, json.JSONDecodeError):
        status = {}

    status.update(
        {
            "schema_version": str(status.get("schema_version") or "2026.02"),
            "status_version": "2.2",
            "mode": "eventide",
            "generated_at": stamp,
        }
    )
    metadata = status.get("metadata") if isinstance(status.get("metadata"), dict) else {}
    metadata.update(
        {
            "project": "Acacia-Garden-AI-Worldbuilding-Codex",
            "keeper_seal": "HKX277206",
            "generated_at": stamp,
            "last_pruning": stamp[:10],
            "current_state_rule": (
                "Current paths are rebuilt from the live tree; historical paths belong in Git history."
            ),
        }
    )
    status["metadata"] = metadata

    status["canonical_files"] = {
        "status": "STATUS.json",
        "schema": "STATUS.schema.json",
        "machine_index": "machine-index.json",
        "docs_urls": "docs/docs_urls.html",
        "novellas_index": "docs/Novellas/garden_index.json",
    }

    for key, directory in PATH_SECTIONS.items():
        status[key] = paths(directory, {".md", ".html", ".json"})

    regions = {name: len(files(directory)) for name, directory in COUNT_REGIONS.items()}
    total = sum(regions.values())
    cycles = {entry["cycle"] for entry in entries if entry.get("cycle") is not None}
    status["core_nodes"] = {
        "counts": {
            "books_indexed": len(entries),
            "long_form_sources_indexed": len(entries),
            "cycles_represented": len(cycles),
            "total_nodes": total,
            "structural_nodes_counted": total,
        },
        "regions": regions,
        "count_scope": (
            "All files inside the explicitly listed structural regions; not a whole-repository file count."
        ),
    }

    expected = [STATUS, SCHEMA, MACHINE_INDEX, DOCS / "docs_urls.html"]
    missing_files = [p.relative_to(ROOT).as_posix() for p in expected if not p.exists()]
    status["safety"] = {
        "health": {
            "missing_files": missing_files,
            "warnings": ([] if DOCS_URLS.exists() else ["docs/docs_urls.json is absent."]),
            "last_checked_utc": stamp,
        }
    }

    archive = archive_proof()
    archive["last_checked_utc"] = stamp
    nav = navigation_proof()
    nav["last_checked_utc"] = stamp
    status["verification"] = {
        "archives": archive,
        "navigation": nav,
        "indexes": {
            "docs_urls_count": docs_urls_count(),
            "docs_urls_present": DOCS_URLS.exists(),
            "machine_index_present": MACHINE_INDEX.exists(),
            "status_schema_present": SCHEMA.exists(),
        },
        "last_verified_utc": stamp,
    }

    growth = status.get("growth")
    if not isinstance(growth, dict):
        growth = {"open": [], "completed": [], "blocked": []}
    growth.pop("prompts", None)
    status["growth"] = growth
    status["notes"] = (
        "Generated current-state description. AUTHORITY.json and source files outrank "
        "generated summaries. Deleted or superseded paths are not carried forward."
    )
    return status


def main() -> int:
    stamp = now_utc()
    entries = novella_inventory(stamp)
    write_json(STATUS, build_status(stamp, entries))
    print("Current Garden state and Novellas inventory rebuilt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
