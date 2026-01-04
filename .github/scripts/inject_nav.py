#!/usr/bin/env python3
"""
Injects nav_block.html into HTML pages (GitHub Pages safe).
- Inserts nav right after <body> tag (preferred).
- If no <body>, inserts after <html> or at top.
- Idempotent: won't inject twice (marker-based + nav signature).
- Skips excluded folders (Archives, big generated chunks, etc).
"""

from __future__ import annotations
import os
import re
from pathlib import Path

REPO_ROOT = Path(".")

NAV_PATH = REPO_ROOT / "nav_block.html"
MARKER_START = "<!-- ACACIA_NAV_INJECTED:START -->"
MARKER_END   = "<!-- ACACIA_NAV_INJECTED:END -->"

# Folders to skip (you can add more)
EXCLUDE_DIR_PARTS = {
    ".git",
    ".github",
    "node_modules",
    "dist",
    "build",
    "docs/Archives",  # monolith chunks
}

# Files to skip by name pattern (optional)
EXCLUDE_FILE_REGEXES = [
    re.compile(r"CODEX_MONOLITH_CHUNK_", re.IGNORECASE),
]

def is_excluded(path: Path) -> bool:
    p = str(path).replace("\\", "/")

    for part in EXCLUDE_DIR_PARTS:
        if f"/{part}/" in f"/{p}/" or p.startswith(part + "/"):
            return True

    for rx in EXCLUDE_FILE_REGEXES:
        if rx.search(path.name):
            return True

    return False

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")

def inject_into_html(html: str, nav_html: str) -> tuple[str, bool]:
    # Already injected?
    if MARKER_START in html and MARKER_END in html:
        return html, False
    if "class=\"ag-nav\"" in html and "ACACIA · GARDEN · 2026" in html:
        # Signature check in case marker missing
        return html, False

    nav_block = f"\n{MARKER_START}\n{nav_html.strip()}\n{MARKER_END}\n"

    # Preferred: right after <body ...>
    m = re.search(r"<body[^>]*>", html, flags=re.IGNORECASE)
    if m:
        insert_at = m.end()
        return html[:insert_at] + nav_block + html[insert_at:], True

    # Fallback: after <html ...>
    m = re.search(r"<html[^>]*>", html, flags=re.IGNORECASE)
    if m:
        insert_at = m.end()
        return html[:insert_at] + nav_block + html[insert_at:], True

    # Last resort: top of file
    return nav_block + html, True

def main() -> int:
    if not NAV_PATH.exists():
        raise SystemExit(f"Missing {NAV_PATH}. Create it first (you already did).")

    nav_html = read_text(NAV_PATH)

    changed = 0
    scanned = 0

    for path in REPO_ROOT.rglob("*.html"):
        if is_excluded(path):
            continue

        # Don't inject into the nav file itself
        if path.name.lower() == "nav_block.html":
            continue

        scanned += 1
        original = read_text(path)

        updated, did = inject_into_html(original, nav_html)
        if did and updated != original:
            write_text(path, updated)
            changed += 1

    print(f"Scanned: {scanned} HTML files")
    print(f"Injected nav into: {changed} files")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
