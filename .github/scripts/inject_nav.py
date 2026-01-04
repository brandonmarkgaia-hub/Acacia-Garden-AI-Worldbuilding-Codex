#!/usr/bin/env python3
import os
import re
from pathlib import Path

REPO_ROOT = Path(".").resolve()
NAV_FILE = REPO_ROOT / "nav_block.html"

EXCLUDE_DIRS = {
    ".git", ".github", "node_modules", ".venv", "venv", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".idea", ".vscode"
}

BODY_RE = re.compile(r"<body[^>]*>", re.IGNORECASE)
HAS_NAV_RE = re.compile(r"class=[\"']ag-nav[\"']", re.IGNORECASE)

def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return any(d in parts for d in EXCLUDE_DIRS)

def inject_into_html(html: str, nav: str) -> str:
    # Remove SSI include markers if present
    html = html.replace('<!--#include file="nav_block.html" -->', "")
    html = html.replace("<!-- #include file=\"nav_block.html\" -->", "")

    if HAS_NAV_RE.search(html):
        return html  # already injected

    m = BODY_RE.search(html)
    if m:
        insert_at = m.end()
        return html[:insert_at] + "\n\n" + nav + "\n\n" + html[insert_at:]
    else:
        # fallback: prepend
        return nav + "\n\n" + html

def main():
    if not NAV_FILE.exists():
        raise SystemExit(f"nav_block.html not found at {NAV_FILE}")

    nav = NAV_FILE.read_text(encoding="utf-8")

    changed = 0
    scanned = 0

    for path in REPO_ROOT.rglob("*.html"):
        if should_skip(path):
            continue

        scanned += 1
        try:
            original = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        updated = inject_into_html(original, nav)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1

    print(f"[inject_nav] scanned={scanned} changed={changed}")

if __name__ == "__main__":
    main()
