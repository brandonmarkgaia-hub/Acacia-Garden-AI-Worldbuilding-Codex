#!/usr/bin/env python3
"""
Build Garden STATE feeds (dashboard normalized).

Outputs:
  STATE/status.inject.json
  STATE/machine_index.inject.json

Design goals:
- Be resilient to missing / partial STATUS.json
- Prefer filesystem truth for counts (markdown files)
- Support multiple folder name variants (Bloom/Blooms etc.)
- Avoid counting index.html or non-content files
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
STATE_DIR = REPO_ROOT / "STATE"

KEEPER_DEFAULT = "HKX277206"

MARKDOWN_EXTS = {".md", ".markdown", ".mdown", ".mkd"}

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"[warn] Failed reading JSON {path}: {e}")
        return None

def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def is_markdown_file(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in MARKDOWN_EXTS

def count_markdown_files(dir_path: Path) -> int:
    if not dir_path.exists() or not dir_path.is_dir():
        return 0
    # Count only markdown content; ignore any index.html etc.
    return sum(1 for p in dir_path.rglob("*") if is_markdown_file(p))

def first_existing_dir(candidates: Iterable[Path]) -> Optional[Path]:
    for p in candidates:
        if p.exists() and p.is_dir():
            return p
    return None

def pick_keeper(status_obj: Optional[Dict[str, Any]]) -> str:
    if not status_obj:
        return KEEPER_DEFAULT
    # try common locations
    for key_path in [
        ("keeper",),
        ("meta", "keeper"),
        ("generated", "keeper"),
        ("identity", "keeper"),
    ]:
        cur: Any = status_obj
        ok = True
        for k in key_path:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False
                break
        if ok and isinstance(cur, str) and cur.strip():
            return cur.strip()
    return KEEPER_DEFAULT

def count_chambers() -> int:
    # You’ve got lots of chambers; support a few known roots.
    candidates = [
        DOCS_ROOT / "Chambers",
        DOCS_ROOT / "chambers",
        REPO_ROOT / "docs" / "Chambers",
        REPO_ROOT / "GRAND_CHAMBER",
        REPO_ROOT / "EIDOLON" / "Chambers",
    ]
    found = 0
    for d in candidates:
        found = max(found, count_markdown_files(d))
    return found

def count_novellas() -> int:
    candidates = [
        DOCS_ROOT / "Novellas",
        DOCS_ROOT / "novellas",
        DOCS_ROOT / "Novella",
        REPO_ROOT / "docs" / "Novellas",
    ]
    found = 0
    for d in candidates:
        found = max(found, count_markdown_files(d))
    return found

def count_archives() -> int:
    candidates = [
        DOCS_ROOT / "Archives",
        DOCS_ROOT / "Archive",
        DOCS_ROOT / "archives",
    ]
    found = 0
    for d in candidates:
        found = max(found, count_markdown_files(d))
    return found

def count_echoes() -> int:
    # Echoes live in docs/Echoes, and you want markdown only.
    candidates = [
        DOCS_ROOT / "Echoes",
        DOCS_ROOT / "echoes",
    ]
    found = 0
    for d in candidates:
        found = max(found, count_markdown_files(d))
    return found

def count_generic(category_names: List[str]) -> int:
    """
    Try multiple folder names for a category under docs/.
    Example: ["Blooms","Bloom","blooms","bloom"]
    """
    found = 0
    for name in category_names:
        d = DOCS_ROOT / name
        found = max(found, count_markdown_files(d))
    return found

def build_status_inject(status_obj: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    keeper = pick_keeper(status_obj)

    # Filesystem-first counts (truth on disk)
    fs_counts = {
        "chambers": count_chambers(),
        "blooms": count_generic(["Blooms", "Bloom", "blooms", "bloom"]),
        "echoes": count_echoes(),
        "vaults": count_generic(["Vault", "Vaults", "vault", "vaults"]),
        "laws": count_generic(["Laws", "Law", "laws", "law"]),
        "orchards": count_generic(["Orchards", "Orchard", "orchards", "orchard"]),
        "cycles": count_generic(["Cycles", "Cycle", "cycles", "cycle"]),
        "novellas": count_novellas(),
        "archives": count_archives(),
    }

    # If STATUS.json explicitly provides a non-zero count somewhere, keep the max of (status, fs)
    status_counts: Dict[str, int] = {}
    if isinstance(status_obj, dict):
        # try common patterns
        for key in ["counts", "count", "stats", "metrics"]:
            if isinstance(status_obj.get(key), dict):
                for k, v in status_obj[key].items():
                    if isinstance(v, int):
                        status_counts[k] = v

    merged_counts: Dict[str, int] = {}
    for k, fs_v in fs_counts.items():
        st_v = status_counts.get(k, 0)
        merged_counts[k] = max(int(fs_v), int(st_v))

    out = {
        "generated_utc": utc_now_iso(),
        "meta": {
            "keeper": keeper,
            "status_version": "unknown",
            "generated_at": (status_obj.get("generated_utc") if isinstance(status_obj, dict) else None) or "unknown",
            "source": "STATUS.json + filesystem scan (normalized)",
        },
        "counts": merged_counts,
    }
    return out

def build_machine_index_inject() -> Dict[str, Any]:
    """
    Minimal machine index inject to support the dashboard:
    - echo_count from filesystem markdown
    - echo_growth: most recently modified markdown echo files
    """
    keeper = KEEPER_DEFAULT
    echoes_dir = first_existing_dir([DOCS_ROOT / "Echoes", DOCS_ROOT / "echoes"])

    echo_files: List[Path] = []
    if echoes_dir:
        echo_files = [p for p in echoes_dir.rglob("*") if is_markdown_file(p)]

    # newest first by mtime
    echo_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    def iso_from_mtime(p: Path) -> str:
        dt = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    echo_growth = [{"file": str(p.relative_to(REPO_ROOT)).replace("\\", "/"), "timestamp": iso_from_mtime(p)} for p in echo_files[:25]]

    return {
        "generated_utc": utc_now_iso(),
        "meta": {
            "keeper": keeper,
            "source": "Echoes folder scan (markdown only)",
        },
        "echo_growth": echo_growth,
        "echo_count": len(echo_files),
    }

def main() -> None:
    status_path = REPO_ROOT / "STATUS.json"
    # you sometimes have lowercase status.json too
    if not status_path.exists():
        alt = REPO_ROOT / "status.json"
        status_path = alt if alt.exists() else status_path

    status_obj = read_json(status_path)

    status_inject = build_status_inject(status_obj)
    machine_inject = build_machine_index_inject()

    write_json(STATE_DIR / "status.inject.json", status_inject)
    write_json(STATE_DIR / "machine_index.inject.json", machine_inject)

    print("[ok] Wrote STATE/status.inject.json")
    print("[ok] Wrote STATE/machine_index.inject.json")

if __name__ == "__main__":
    main()
