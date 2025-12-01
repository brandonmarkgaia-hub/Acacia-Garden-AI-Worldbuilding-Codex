#!/usr/bin/env python3
"""
build_garden_index.py

Scan docs/Novellas for Garden book markdown files and generate:
- docs/Novellas/garden_index.json
- docs/Novellas/GARDEN_MASTER_INDEX.md

Assumptions:
- Each book file is a .md in docs/Novellas/
- The first heading contains 'BOOK <ROMAN>' and a title, e.g.:

  # 📘 BOOK XXII — The Garden Physics & Mathematics Codex

This script is safe to re-run any time.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # adjust if you put script elsewhere
NOVELLAS_DIR = ROOT / "docs" / "Novellas"
INDEX_JSON = NOVELLAS_DIR / "garden_index.json"
MASTER_MD = NOVELLAS_DIR / "GARDEN_MASTER_INDEX.md"

ROMAN_MAP = {
    "I": 1, "V": 5, "X": 10, "L": 50, "C": 100
}

def roman_to_int(s: str) -> int:
    s = s.strip().upper()
    total = 0
    prev = 0
    for ch in reversed(s):
        val = ROMAN_MAP.get(ch, 0)
        if val < prev:
            total -= val
        else:
            total += val
        prev = val
    return total

def extract_book_info(path: Path):
    """
    Return dict: {"id": int, "title": str, "file": "relative/path.md"} or None
    """
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

    # look for first heading line
    first_heading = None
    for line in text.splitlines():
        if line.strip().startswith("#"):
            first_heading = line.strip().lstrip("#").strip()
            break

    if not first_heading:
        return None

    # Try to parse "BOOK XX" and title
    # Examples:
    # "📘 BOOK XXII — The Garden Physics & Mathematics Codex"
    # "BOOK XXV — The Orchard of Consequence"
    m = re.search(r"BOOK\s+([IVXLC]+)\s+[—-]\s+(.+)", first_heading, re.IGNORECASE)
    if not m:
        return None

    roman = m.group(1)
    title = m.group(2).strip()
    num = roman_to_int(roman)

    rel = path.relative_to(ROOT).as_posix()
    return {"id": num, "title": title, "file": rel}

def build_index():
    if not NOVELLAS_DIR.exists():
        raise SystemExit(f"Directory not found: {NOVELLAS_DIR}")

    books = []
    for md in sorted(NOVELLAS_DIR.glob("*.md")):
        if md.name.upper().startswith("GARDEN_MASTER_INDEX"):
            continue
        info = extract_book_info(md)
        if info:
            books.append(info)

    # sort by id
    books.sort(key=lambda b: b["id"])

    index = {
        "garden_codex": {
            "keeper": "HKX277206",
            "total_books": len(books),
            "books": [
                {"id": b["id"], "title": b["title"], "file": b["file"]}
                for b in books
            ]
        }
    }

    INDEX_JSON.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {INDEX_JSON} with {len(books)} books.")

    # Now build a nice human-readable master index
    lines = []
    lines.append("# 🌳 The Garden Codex — Master Index\n")
    lines.append(f"_Automatically generated from docs/Novellas by build_garden_index.py._\n")

    for b in books:
        lines.append(f"- **Book {b['id']} – {b['title']}**  ")
        lines.append(f"  - `{b['file']}`")

    MASTER_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {MASTER_MD}")

if __name__ == "__main__":
    build_index()
