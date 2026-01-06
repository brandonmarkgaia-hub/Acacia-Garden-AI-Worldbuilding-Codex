#!/usr/bin/env python3
"""
tools/garden_lore_helper.py

Platinum-safe STATUS writer.

Goals:
- Preserve Platinum STATUS constitution (identity/entrypoints/invariants/automation).
- Update only dynamic facts (counts, health checks, generated timestamps).
- Generate docs/Novellas/garden_index.json (books index) as before.
- Generate tools/echo_index.json (optional) as before.
- Never reintroduce legacy "growth.prompts" or overwrite STATUS into old schema.

No external dependencies.
"""

from __future__ import annotations

from pathlib import Path
import json
import re
import datetime as dt
from typing import Any, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parent.parent

NOVELLAS_DIR = ROOT / "docs" / "Novellas"
DOCS_ROOT = ROOT / "docs"
TOOLS_DIR = ROOT / "tools"
TOOLS_DIR.mkdir(parents=True, exist_ok=True)

STATUS_PATH = ROOT / "STATUS.json"
MACHINE_INDEX_PATH = ROOT / "machine-index.json"
SCAN_REPORT_PATH = ROOT / "tools" / "garden_scan_report.json"
DOCS_URLS_HTML_PATH = ROOT / "docs" / "docs_urls.html"
DOCS_URLS_JSON_PATH = ROOT / "docs" / "docs_urls.json"

ARCHIVES_DIR = ROOT / "docs" / "Archives"
BASE_HREF = "/Acacia-Garden-AI-Worldbuilding-Codex/"
BASE_TAG_NEEDLE = f'<base href="{BASE_HREF}"'


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_title(path: Path) -> str:
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

    cycle = None
    volume = None

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


def build_echo_index(now_iso: str) -> None:
    """
    Optional Echo folder index. Safe if empty.
    """
    echo_root = ROOT / "docs" / "Echoes"
    echo_files = []

    if echo_root.is_dir():
        for md in sorted(echo_root.glob("*.md")):
            title = load_title(md)
            rel_path = md.relative_to(ROOT).as_posix()
            echo_files.append({"title": title, "path": rel_path})

    out = TOOLS_DIR / "echo_index.json"
    out.write_text(
        json.dumps({"generated_at": now_iso, "echoes": echo_files}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def count_files_in_dir(dir_path: Path, exts=None) -> int:
    if not dir_path.exists():
        return 0
    if exts is None:
        return sum(1 for p in dir_path.rglob("*") if p.is_file())
    exts = {e.lower() for e in exts}
    return sum(1 for p in dir_path.rglob("*") if p.is_file() and p.suffix.lower() in exts)


def expected_paths_health(now_iso: str) -> Dict[str, Any]:
    """
    Health checks for canonical artifacts and common GH Pages pitfalls.
    Returns dict with missing_files + warnings + last_checked_utc.
    """
    expected = [
        MACHINE_INDEX_PATH,
        STATUS_PATH,
        ROOT / "STATUS.schema.json",
        DOCS_URLS_HTML_PATH,
        SCAN_REPORT_PATH,
    ]

    missing = [p.relative_to(ROOT).as_posix() for p in expected if not p.exists()]

    # Folder links from dashboard that need index.html to not 404
    folder_indexes = [
        ROOT / "docs" / "Chambers" / "index.html",
        ROOT / "docs" / "Vaults" / "index.html",
        ROOT / "docs" / "Echoes" / "index.html",
        ROOT / "docs" / "GardenOS" / "index.html",
    ]
    folder_missing = [p.relative_to(ROOT).as_posix() for p in folder_indexes if not p.exists()]

    warnings: List[str] = []
    if folder_missing:
        warnings.append(
            "Missing docs folder index pages (GH Pages cannot list folders): " + ", ".join(folder_missing)
        )

    # docs_urls.json optional but nice to have
    if not DOCS_URLS_JSON_PATH.exists():
        warnings.append("docs/docs_urls.json missing (optional but recommended for tooling).")

    return {
        "missing_files": missing,
        "warnings": warnings,
        "last_checked_utc": now_iso,
    }


def scan_archives_base_href_missing() -> Tuple[int, int, int]:
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
    (If you already committed your Platinum STATUS, we preserve it.)
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
                "repository": "brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex",
                "branch": "main",
            },
        },
        "entrypoints": {
            "root": "/Acacia-Garden-AI-Worldbuilding-Codex/",
            "map": "/Acacia-Garden-AI-Worldbuilding-Codex/map.html",
            "docs_index": "/Acacia-Garden-AI-Worldbuilding-Codex/docs/index.html",
            "docs_urls": "/Acacia-Garden-AI-Worldbuilding-Codex/docs/docs_urls.html",
        },
        "canonical_files": {
            "status": "STATUS.json",
            "schema": "STATUS.schema.json",
            "machine_index": "machine-index.json",
            "scan_report": "tools/garden_scan_report.json",
            "docs_urls": "docs/docs_urls.html",
            "novellas_index": "docs/Novellas/garden_index.json",
        },
        "core_nodes": {
            "counts": {"books_indexed": 0, "cycles_represented": 0},
            "regions": {},
        },
        "verification": {
            "last_verified_utc": None,
            "archives": {"total_html": 0, "with_base_href": 0, "missing_base_href": 0, "verified": False},
            "navigation": {"map_button_present": False, "docs_urls_count": 0, "verified": False},
            "indexes": {"machine_index_in_sync": False, "docs_urls_in_sync": False},
        },
        "growth": {"open": [], "completed": [], "blocked": []},
        "safety": {"health": {"missing_files": [], "warnings": [], "last_checked_utc": None}},
        "notes": "Autogenerated by tools/garden_lore_helper.py (platinum-safe eventide mode)",
    }


def upsert_growth_archives_prompt(status: Dict[str, Any], missing_base: int, total_archives: int, now_iso: str) -> None:
    """
    If Archives exist AND missing base href > 0, ensure a structured growth.open item exists.
    If missing_base == 0, remove any matching open item (stale prompt cleanup).
    """
    growth = ensure_dict(status, "growth")
    open_list = ensure_list(growth, "open")

    prompt_id = "archives_base_href"
    # normalize open entries into list of dicts; ignore strings
    normalized: List[Dict[str, Any]] = [x for x in open_list if isinstance(x, dict)]
    others: List[Any] = [x for x in open_list if not isinstance(x, dict)]

    def is_match(item: Dict[str, Any]) -> bool:
        return item.get("id") == prompt_id

    normalized = [x for x in normalized if not is_match(x)]

    if total_archives > 0 and missing_base > 0:
        normalized.append(
            {
                "id": prompt_id,
                "title": "Fix Archives base href",
                "status": "open",
                "created_at": now_iso,
                "scope": "docs/Archives/*.html",
                "criteria": f"missing_base_href == 0 (currently {missing_base} of {total_archives})",
                "suggestion": f"Inject <base href='{BASE_HREF}'> into docs/Archives/*.html",
            }
        )

    # reassemble (keep non-dict legacy entries if any)
    growth["open"] = normalized + others


def main() -> None:
    now_iso = utc_now_iso()

    # Build books
    books = build_books()

    # Write Novellas index used by the site
    NOVELLAS_DIR.mkdir(parents=True, exist_ok=True)
    out_index = NOVELLAS_DIR / "garden_index.json"
    out_index.write_text(
        json.dumps({"generated_at": now_iso, "books": books}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Echo index (optional)
    build_echo_index(now_iso)

    # Load existing STATUS if present; otherwise create minimal platinum
    if STATUS_PATH.exists():
        try:
            status = read_json(STATUS_PATH)
            if not isinstance(status, dict):
                status = make_platinum_minimal(now_iso)
        except Exception:
            status = make_platinum_minimal(now_iso)
    else:
        status = make_platinum_minimal(now_iso)

    # Update only dynamic facts
    status["generated_at"] = now_iso

    # Canonical file pointers (do not delete user-added keys)
    canonical = ensure_dict(status, "canonical_files")
    canonical.setdefault("status", "STATUS.json")
    canonical.setdefault("schema", "STATUS.schema.json")
    canonical.setdefault("machine_index", "machine-index.json")
    canonical.setdefault("scan_report", "tools/garden_scan_report.json")
    canonical.setdefault("docs_urls", "docs/docs_urls.html")
    canonical.setdefault("novellas_index", "docs/Novellas/garden_index.json")

    # Core counts
    cycles = sorted({b["cycle"] for b in books if b.get("cycle") is not None})
    core_nodes = ensure_dict(status, "core_nodes")
    counts = ensure_dict(core_nodes, "counts")
    counts["books_indexed"] = len(books)
    counts["cycles_represented"] = len(cycles)

    # Region counts (your “meat”)
    regions = ensure_dict(core_nodes, "regions")
    regions["docs/Chambers"] = count_files_in_dir(ROOT / "docs" / "Chambers", exts=[".md", ".html", ".json"])
    regions["docs/Echoes"] = count_files_in_dir(ROOT / "docs" / "Echoes", exts=[".md", ".html", ".json"])
    regions["docs/Vaults"] = count_files_in_dir(ROOT / "docs" / "Vaults", exts=[".md", ".html", ".json"])
    regions["docs/GardenOS"] = count_files_in_dir(ROOT / "docs" / "GardenOS", exts=[".md", ".html", ".json"])
    regions["docs/Novellas"] = len(books)
    regions["docs/Archives"] = count_files_in_dir(ROOT / "docs" / "Archives", exts=[".html"])
    regions["tools"] = count_files_in_dir(ROOT / "tools", exts=[".py", ".json", ".html", ".md"])
    regions[".github/workflows"] = count_files_in_dir(ROOT / ".github" / "workflows", exts=[".yml", ".yaml"])

    # Safety health
    safety = ensure_dict(status, "safety")
    health = ensure_dict(safety, "health")
    fresh_health = expected_paths_health(now_iso)
    health["missing_files"] = fresh_health["missing_files"]
    health["warnings"] = fresh_health["warnings"]
    health["last_checked_utc"] = fresh_health["last_checked_utc"]

    # Growth: structured prompt only if actually needed (no more stale prompts)
    total_archives, _, missing_base = scan_archives_base_href_missing()
    upsert_growth_archives_prompt(status, missing_base=missing_base, total_archives=total_archives, now_iso=now_iso)

    # Remove legacy "growth.prompts" if it exists (this is how stale desires are born)
    if isinstance(status.get("growth"), dict) and "prompts" in status["growth"]:
        status["growth"].pop("prompts", None)

    # Ensure notes mention platinum-safe mode
    status["notes"] = "Autogenerated by tools/garden_lore_helper.py (platinum-safe eventide mode)"

    write_json(STATUS_PATH, status)
    print("✅ STATUS.json updated (platinum-safe) + Novellas index written.")


if __name__ == "__main__":
    main()
