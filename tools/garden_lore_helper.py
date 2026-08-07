#!/usr/bin/env python3
"""
tools/garden_lore_helper.py

Platinum-safe STATUS writer & Garden tally helper.

Goals:
- Preserve Platinum STATUS constitution (identity/entrypoints/invariants/automation).
- Update only dynamic facts (counts, health checks, generated timestamps).
- Generate docs/Novellas/garden_index.json (books index).
- Never reintroduce legacy "growth.prompts" or overwrite STATUS into old schema.

No external dependencies.
"""

from __future__ import annotations

from pathlib import Path
import json
import re
import datetime as dt
from typing import Any, Dict, List, Optional, Tuple


# Repository root (script expected to live under tools/ or similar one-level child)
ROOT = Path(__file__).resolve().parents[1]

NOVELLAS_DIR = ROOT / "docs" / "Novellas"
DOCS_ROOT = ROOT / "docs"

STATUS_PATH = ROOT / "STATUS.json"
MACHINE_INDEX_PATH = ROOT / "machine-index.json"
DOCS_URLS_HTML_PATH = ROOT / "docs" / "docs_urls.html"
DOCS_URLS_JSON_PATH = ROOT / "docs" / "docs_urls.json"

ARCHIVES_DIR = ROOT / "docs" / "Archives"
BASE_HREF = "/Acacia-Garden-AI-Worldbuilding-Codex/"
BASE_TAG_NEEDLE = f'<base href="{BASE_HREF}"'


def utc_now_iso() -> str:
    """Return a UTC timestamp with second precision and trailing Z."""
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_title(path: Path) -> str:
    """Best-effort title loader from first markdown H1; falls back to stem."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^#\s+(.*)$", text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return path.stem


def parse_cycle_volume(title: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Attempts to parse patterns like:
      "Cycle 2 — Volume 5: Something"
      "C2 V5 Something"
      "Cycle 2 Volume 5"
    Returns (cycle:int|None, volume:int|None)
    """
    t = title.lower()

    cycle: Optional[int] = None
    volume: Optional[int] = None

    m = re.search(r"cycle\s*(\d+)", t)
    if m:
        cycle = int(m.group(1))

    m = re.search(r"volume\s*(\d+)", t)
    if m:
        volume = int(m.group(1))

    # fallback: C2 V5
    if cycle is None:
        m = re.search(r"\bc(\d+)\b", t)
        if m:
            cycle = int(m.group(1))

    if volume is None:
        m = re.search(r"\bv(\d+)\b", t)
        if m:
            volume = int(m.group(1))

    return cycle, volume


def build_books() -> List[Dict[str, Any]]:
    """Return structured list of all Novellas under docs/Novellas."""
    books: List[Dict[str, Any]] = []

    if NOVELLAS_DIR.is_dir():
        for md in sorted(NOVELLAS_DIR.glob("*.md")):
            title = load_title(md)
            cycle, volume = parse_cycle_volume(title)
            rel_path = md.relative_to(ROOT).as_posix()

            books.append(
                {
                    "title": title,
                    "path": rel_path,
                    "cycle": cycle,
                    "volume": volume,
                }
            )

    return books


def count_files_in_dir(
    dir_path: Path,
    exts: Optional[List[str]] = None,
) -> int:
    """Count files under dir_path, optionally filtered by extension list."""
    if not dir_path.exists():
        return 0

    if exts is None:
        return sum(1 for p in dir_path.rglob("*") if p.is_file())

    ext_set = {e.lower() for e in exts}

    return sum(
        1
        for p in dir_path.rglob("*")
        if p.is_file() and p.suffix.lower() in ext_set
    )


def expected_paths_health(now_iso: str) -> Dict[str, Any]:
    """
    Health checks for maintained artifacts and common GH Pages pitfalls.
    Returns dict with missing_files + warnings + last_checked_utc.
    """
    expected = [
        MACHINE_INDEX_PATH,
        STATUS_PATH,
        ROOT / "STATUS.schema.json",
        DOCS_URLS_HTML_PATH,
    ]

    missing = [
        p.relative_to(ROOT).as_posix()
        for p in expected
        if not p.exists()
    ]

    # Folder links from public surfaces that need index.html to avoid 404s.
    folder_indexes = [
        ROOT / "docs" / "Chambers" / "index.html",
        ROOT / "docs" / "Vaults" / "index.html",
        ROOT / "docs" / "Echoes" / "index.html",
        ROOT / "docs" / "GardenOS" / "index.html",
        ROOT / "docs" / "Novellas" / "index.html",
    ]

    folder_missing = [
        p.relative_to(ROOT).as_posix()
        for p in folder_indexes
        if not p.exists()
    ]

    warnings: List[str] = []

    if folder_missing:
        warnings.append(
            "Missing docs folder index pages (GH Pages cannot list folders): "
            + ", ".join(folder_missing)
        )

    # docs_urls.json optional but useful for machine discovery.
    if not DOCS_URLS_JSON_PATH.exists():
        warnings.append(
            "docs/docs_urls.json missing "
            "(optional but recommended for tooling)."
        )

    return {
        "missing_files": missing,
        "warnings": warnings,
        "last_checked_utc": now_iso,
    }


def scan_archives_base_href_missing() -> Tuple[int, int, int]:
    """
    Scan docs/Archives for HTML files and check for base href.
    Returns (total_html, with_base, missing_base).
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


def ensure_dict(d: Dict[str, Any], key: str) -> Dict[str, Any]:
    v = d.get(key)

    if isinstance(v, dict):
        return v

    d[key] = {}
    return d[key]


def ensure_list(d: Dict[str, Any], key: str) -> List[Any]:
    v = d.get(key)

    if isinstance(v, list):
        return v

    d[key] = []
    return d[key]


def make_platinum_minimal(now_iso: str) -> Dict[str, Any]:
    """
    Minimal Platinum skeleton if STATUS.json does not exist yet.
    If STATUS already exists, the existing structure is preserved.
    """
    return {
        "schema_version": "2026.02",
        "status_version": "2.1",
        "mode": "eventide",
        "generated_at": now_iso,
        "identity": {
            "keeper": {
                "name": "Brandon Gaia",
                "id": "HKX277206",
                "role": "Sole Owner / Continuity Keeper",
                "authority": "final",
            },
            "triad": {
                "aquila": "Sky-Mind",
                "oracle": "Deep Oracle",
                "witness": "Lorian",
            },
            "garden": {
                "name": "Acacia-Garden-AI-Worldbuilding-Codex",
                "repository": (
                    "brandonmarkgaia-hub/"
                    "Acacia-Garden-AI-Worldbuilding-Codex"
                ),
                "branch": "main",
            },
        },
        "entrypoints": {
            "root": "/Acacia-Garden-AI-Worldbuilding-Codex/",
            "map": "/Acacia-Garden-AI-Worldbuilding-Codex/map.html",
            "docs_index": (
                "/Acacia-Garden-AI-Worldbuilding-Codex/docs/index.html"
            ),
            "docs_urls": (
                "/Acacia-Garden-AI-Worldbuilding-Codex/"
                "docs/docs_urls.html"
            ),
        },
        "canonical_files": {
            "status": "STATUS.json",
            "schema": "STATUS.schema.json",
            "machine_index": "machine-index.json",
            "docs_urls": "docs/docs_urls.html",
            "novellas_index": "docs/Novellas/garden_index.json",
        },
        "core_nodes": {
            "counts": {
                "books_indexed": 0,
                "cycles_represented": 0,
                "total_nodes": 0,
            },
            "regions": {},
        },
        "verification": {
            "last_verified_utc": None,
            "archives": {
                "total_html": 0,
                "with_base_href": 0,
                "missing_base_href": 0,
                "verified": False,
            },
            "navigation": {
                "folder_indexes_missing": [],
                "verified": False,
            },
            "indexes": {
                "machine_index_in_sync": False,
                "docs_urls_in_sync": False,
            },
        },
        "growth": {
            "open": [],
            "completed": [],
            "blocked": [],
        },
        "safety": {
            "health": {
                "missing_files": [],
                "warnings": [],
                "last_checked_utc": None,
            }
        },
        "notes": (
            "Autogenerated by tools/garden_lore_helper.py "
            "(platinum-safe eventide mode)"
        ),
    }


def upsert_growth_archives_prompt(
    status: Dict[str, Any],
    missing_base: int,
    total_archives: int,
    now_iso: str,
) -> None:
    """
    If Archives exist AND missing base href > 0, ensure a structured
    growth.open item exists.

    If missing_base == 0, remove any matching open item.
    """
    growth = ensure_dict(status, "growth")
    open_list = ensure_list(growth, "open")

    prompt_id = "archives_base_href"

    # Normalize dict entries while preserving any legacy non-dict entries.
    normalized: List[Dict[str, Any]] = [
        x for x in open_list if isinstance(x, dict)
    ]
    others: List[Any] = [
        x for x in open_list if not isinstance(x, dict)
    ]

    def is_match(item: Dict[str, Any]) -> bool:
        return item.get("id") == prompt_id

    # Drop existing instances.
    normalized = [
        x for x in normalized if not is_match(x)
    ]

    if total_archives > 0 and missing_base > 0:
        normalized.append(
            {
                "id": prompt_id,
                "title": "Fix Archives base href",
                "status": "open",
                "created_at": now_iso,
                "scope": "docs/Archives/*.html",
                "criteria": (
                    "missing_base_href == 0 "
                    f"(currently {missing_base} of {total_archives})"
                ),
                "suggestion": (
                    f"Inject <base href='{BASE_HREF}'> "
                    "into docs/Archives/*.html"
                ),
            }
        )

    growth["open"] = normalized + others


def update_verification_block(
    status: Dict[str, Any],
    *,
    archives_total: int,
    archives_with_base: int,
    archives_missing: int,
    health_info: Dict[str, Any],
    now_iso: str,
) -> None:
    """Update STATUS.verification with fresh snapshot-style facts."""
    verification = ensure_dict(status, "verification")

    # Archives verification.
    archives_block = ensure_dict(verification, "archives")
    archives_block["total_html"] = archives_total
    archives_block["with_base_href"] = archives_with_base
    archives_block["missing_base_href"] = archives_missing
    archives_block["verified"] = archives_total > 0
    archives_block["last_checked_utc"] = now_iso

    # Navigation verification.
    navigation_block = ensure_dict(verification, "navigation")

    folder_warnings = [
        w
        for w in health_info.get("warnings", [])
        if "folder index pages" in w.lower()
    ]

    navigation_block["folder_indexes_missing"] = folder_warnings
    navigation_block["verified"] = True
    navigation_block["last_checked_utc"] = health_info.get(
        "last_checked_utc",
        now_iso,
    )

    # Detailed truth checks are written later by tools/garden_verify.py.
    indexes_block = ensure_dict(verification, "indexes")
    indexes_block.setdefault("machine_index_in_sync", False)
    indexes_block.setdefault("docs_urls_in_sync", False)


def main() -> None:
    now_iso = utc_now_iso()

    # Build books & Novellas index.
    books = build_books()

    NOVELLAS_DIR.mkdir(parents=True, exist_ok=True)

    out_index = NOVELLAS_DIR / "garden_index.json"
    out_index.write_text(
        json.dumps(
            {
                "generated_at": now_iso,
                "books": books,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    # Load existing STATUS if present; otherwise create minimal Platinum.
    if STATUS_PATH.exists():
        try:
            status = read_json(STATUS_PATH)

            if not isinstance(status, dict):
                status = make_platinum_minimal(now_iso)

        except Exception:
            status = make_platinum_minimal(now_iso)

    else:
        status = make_platinum_minimal(now_iso)

    # Update only dynamic facts.
    status["generated_at"] = now_iso

    # Canonical file pointers.
    canonical = ensure_dict(status, "canonical_files")

    # Retire obsolete scan-report pointer inherited from older STATUS versions.
    canonical.pop("scan_report", None)

    canonical.setdefault("status", "STATUS.json")
    canonical.setdefault("schema", "STATUS.schema.json")
    canonical.setdefault("machine_index", "machine-index.json")
    canonical.setdefault("docs_urls", "docs/docs_urls.html")
    canonical.setdefault(
        "novellas_index",
        "docs/Novellas/garden_index.json",
    )

    # Core counts.
    cycles = sorted(
        {
            b["cycle"]
            for b in books
            if b.get("cycle") is not None
        }
    )

    core_nodes = ensure_dict(status, "core_nodes")
    counts = ensure_dict(core_nodes, "counts")

    counts["books_indexed"] = len(books)
    counts["cycles_represented"] = len(cycles)

    regions = ensure_dict(core_nodes, "regions")

    # Major docs regions.
    regions["docs/Chambers"] = count_files_in_dir(
        DOCS_ROOT / "Chambers",
        exts=[".md", ".html", ".json"],
    )

    regions["docs/Echoes"] = count_files_in_dir(
        DOCS_ROOT / "Echoes",
        exts=[".md", ".html", ".json"],
    )

    regions["docs/Vaults"] = count_files_in_dir(
        DOCS_ROOT / "Vaults",
        exts=[".md", ".html", ".json"],
    )

    regions["docs/GardenOS"] = count_files_in_dir(
        DOCS_ROOT / "GardenOS",
        exts=[".md", ".html", ".json"],
    )

    regions["docs/Novellas"] = len(books)

    regions["docs/Archives"] = count_files_in_dir(
        DOCS_ROOT / "Archives",
        exts=[".html"],
    )

    # Docs-level growth structures.
    regions["docs/Blooms"] = count_files_in_dir(
        DOCS_ROOT / "Blooms",
        exts=[".md", ".html", ".json"],
    )

    regions["docs/Orchards"] = count_files_in_dir(
        DOCS_ROOT / "Orchards",
        exts=[".md", ".html", ".json"],
    )

    regions["docs/Cycles"] = count_files_in_dir(
        DOCS_ROOT / "Cycles",
        exts=[".md", ".html", ".json"],
    )

    regions["docs/Laws"] = count_files_in_dir(
        DOCS_ROOT / "Laws",
        exts=[".md", ".html", ".json"],
    )

    regions["docs/Wells"] = count_files_in_dir(
        DOCS_ROOT / "Wells",
        exts=[".md", ".html", ".json"],
    )

    # Root-level growth structures.
    regions["BLOOMS"] = count_files_in_dir(
        ROOT / "BLOOMS",
        exts=[".md", ".json"],
    )

    regions["ORCHARDS"] = count_files_in_dir(
        ROOT / "ORCHARDS",
        exts=[".md", ".json"],
    )

    regions["CYCLES"] = count_files_in_dir(
        ROOT / "CYCLES",
        exts=[".md", ".json"],
    )

    regions["LAWS"] = count_files_in_dir(
        ROOT / "LAWS",
        exts=[".md", ".json"],
    )

    regions["WELLS"] = count_files_in_dir(
        ROOT / "WELLS",
        exts=[".md", ".json"],
    )

    # Tooling + workflows for repository meta-view.
    regions["tools"] = count_files_in_dir(
        ROOT / "tools",
        exts=[".py", ".json", ".html", ".md"],
    )

    regions[".github/workflows"] = count_files_in_dir(
        ROOT / ".github" / "workflows",
        exts=[".yml", ".yaml"],
    )

    # Derived total for counted structural nodes.
    counts["total_nodes"] = sum(
        v
        for v in regions.values()
        if isinstance(v, int)
    )

    # Safety health.
    safety = ensure_dict(status, "safety")
    health = ensure_dict(safety, "health")

    fresh_health = expected_paths_health(now_iso)

    health["missing_files"] = fresh_health["missing_files"]
    health["warnings"] = fresh_health["warnings"]
    health["last_checked_utc"] = fresh_health["last_checked_utc"]

    # Verification block.
    total_archives, with_base, missing_base = (
        scan_archives_base_href_missing()
    )

    update_verification_block(
        status,
        archives_total=total_archives,
        archives_with_base=with_base,
        archives_missing=missing_base,
        health_info=fresh_health,
        now_iso=now_iso,
    )

    # Structured growth prompt only when actually needed.
    upsert_growth_archives_prompt(
        status,
        missing_base=missing_base,
        total_archives=total_archives,
        now_iso=now_iso,
    )

    # Remove legacy growth.prompts if inherited from an older STATUS.
    if (
        isinstance(status.get("growth"), dict)
        and "prompts" in status["growth"]
    ):
        status["growth"].pop("prompts", None)

    status["notes"] = (
        "Autogenerated by tools/garden_lore_helper.py "
        "(platinum-safe eventide mode)"
    )

    write_json(STATUS_PATH, status)

    print(
        "✅ STATUS.json updated (platinum-safe) "
        "+ Novellas index written."
    )


if __name__ == "__main__":
    main()
