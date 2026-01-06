#!/usr/bin/env python3
import os
import re
from pathlib import Path

PROJECT_PREFIX = "/Acacia-Garden-AI-Worldbuilding-Codex"
SCRIPT_TAG = f'<script src="{PROJECT_PREFIX}/assets/triad_nav.js" defer></script>'
CSS_TAG    = f'<link rel="stylesheet" href="{PROJECT_PREFIX}/assets/triad_nav.css">'

# Very light touch: add to <head> if missing.
# Do NOT try to rewrite page content; the JS will remove duplicate nav blocks safely.
HEAD_CLOSE_RE = re.compile(r"</head\s*>", re.IGNORECASE)

def patch_html(p: Path) -> bool:
    try:
        raw = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False

    if "<head" not in raw.lower():
        return False

    changed = False

    if "assets/triad_nav.css" not in raw:
        raw = HEAD_CLOSE_RE.sub(CSS_TAG + "\n" + "</head>", raw, count=1)
        changed = True

    if "assets/triad_nav.js" not in raw:
        raw = HEAD_CLOSE_RE.sub(SCRIPT_TAG + "\n" + "</head>", raw, count=1)
        changed = True

    if changed:
        p.write_text(raw, encoding="utf-8")
    return changed

def main():
    root = Path(".")
    html_files = [p for p in root.rglob("*.html") if ".git" not in str(p)]
    touched = 0
    for p in html_files:
        if patch_html(p):
            touched += 1
    print(f"[triad_nav] patched {touched} html files out of {len(html_files)}")

if __name__ == "__main__":
    main()
