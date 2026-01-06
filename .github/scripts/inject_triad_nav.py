#!/usr/bin/env python3
"""
Inject Triad Nav loader into HTML files, safely and idempotently.

- Removes duplicate/old triad_nav.js script tags
- Injects exactly one script tag with a correct relative path from each HTML file
- Prefers insertion before </head>, else before </body>, else at end of file
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable, Tuple

RE_TRIAD_SCRIPT = re.compile(
    r"""<script\b[^>]*\bsrc\s*=\s*["'][^"']*triad_nav\.js[^"']*["'][^>]*>\s*</script>\s*""",
    re.IGNORECASE,
)

RE_HEAD_CLOSE = re.compile(r"</head\s*>", re.IGNORECASE)
RE_BODY_CLOSE = re.compile(r"</body\s*>", re.IGNORECASE)

SKIP_DIRS = {
    ".git",
    ".github",          # we do NOT inject into workflow HTML docs, if any
    "node_modules",
    "vendor",
    "dist",
    "build",
    "__pycache__",
}

def should_skip_path(path: Path) -> bool:
    parts = set(path.parts)
    return any(d in parts for d in SKIP_DIRS)

def html_files(repo_root: Path) -> Iterable[Path]:
    for p in repo_root.rglob("*.html"):
        if should_skip_path(p):
            continue
        # Skip the JS itself (just in case of odd extensions)
        if p.name.lower() == "triad_nav.js":
            continue
        yield p

def rel_script_src(repo_root: Path, html_path: Path) -> str:
    # Compute depth of the HTML file relative to repo root.
    # depth=0 => root file => "assets/triad_nav.js"
    # depth=1 => docs/file.html => "../assets/triad_nav.js"
    # depth=2 => docs/Archives/file.html => "../../assets/triad_nav.js"
    rel = html_path.relative_to(repo_root)
    depth = len(rel.parts) - 1  # file itself doesn't count
    prefix = "" if depth == 0 else "../" * depth
    return f"{prefix}assets/triad_nav.js"

def inject_into_html(text: str, script_src: str) -> Tuple[str, bool]:
    original = text

    # 1) Remove any existing triad_nav.js script tags (dedupe)
    text = RE_TRIAD_SCRIPT.sub("", text)

    # 2) Build the canonical script tag
    script_tag = f'<script src="{script_src}" defer></script>\n'

    # If it already contains exact tag (rare, after removal), avoid double insert
    if script_tag.strip() in text:
        return text, (text != original)

    # 3) Insert before </head> if present
    m = RE_HEAD_CLOSE.search(text)
    if m:
        insert_at = m.start()
        text = text[:insert_at] + script_tag + text[insert_at:]
        return text, (text != original)

    # 4) Else insert before </body>
    m = RE_BODY_CLOSE.search(text)
    if m:
        insert_at = m.start()
        text = text[:insert_at] + script_tag + text[insert_at:]
        return text, (text != original)

    # 5) Else append
    if not text.endswith("\n"):
        text += "\n"
    text += script_tag
    return text, (text != original)

def main() -> int:
    repo_root = Path(".").resolve()
    changed = 0
    scanned = 0

    for p in html_files(repo_root):
        scanned += 1
        try:
            raw = p.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"[WARN] Could not read {p}: {e}")
            continue

        src = rel_script_src(repo_root, p)
        updated, did_change = inject_into_html(raw, src)

        if did_change:
            try:
                p.write_text(updated, encoding="utf-8")
                changed += 1
                print(f"[OK] Injected: {p}  (src={src})")
            except Exception as e:
                print(f"[ERROR] Could not write {p}: {e}")
                return 2

    print(f"\nDone. Scanned {scanned} HTML files. Updated {changed}.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
