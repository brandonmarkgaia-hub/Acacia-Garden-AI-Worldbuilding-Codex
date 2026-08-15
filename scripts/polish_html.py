#!/usr/bin/env python3
"""Deterministically polish Acacia Garden HTML surfaces.

This script performs presentation/infrastructure repairs only. It does not
rewrite Garden canon or body prose except to wrap a legacy HTML fragment as a
complete document. Existing titles, descriptions and content are preserved.
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://brandonmarkgaia-hub.github.io/Acacia-Garden-AI-Worldbuilding-Codex/"
SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "_site"}
ARCHIVES = ("docs/Archives/", "_ROOT_ARCHIVE/")

DOCTYPE_RE = re.compile(r"<!doctype\s+html\s*>", re.I)
HTML_RE = re.compile(r"<html\b", re.I)
HEAD_RE = re.compile(r"<head\b[^>]*>", re.I)
BODY_RE = re.compile(r"<body\b", re.I)
TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.I | re.S)
CHARSET_RE = re.compile(r"<meta\b[^>]*charset\s*=", re.I)
VIEWPORT_RE = re.compile(r"<meta\b[^>]*name\s*=\s*[\"']viewport[\"']", re.I)
DESCRIPTION_RE = re.compile(r"<meta\b[^>]*name\s*=\s*[\"']description[\"']", re.I)
CANONICAL_RE = re.compile(r"<link\b[^>]*rel\s*=\s*[\"'][^\"']*canonical", re.I)
LANG_RE = re.compile(r"<html\b([^>]*)>", re.I)


def is_archive(rel: str) -> bool:
    return any(rel.startswith(prefix) for prefix in ARCHIVES)


def title_from(text: str, rel: str) -> str:
    match = TITLE_RE.search(text)
    if match:
        value = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", match.group(1))).strip()
        if value:
            return html.unescape(value)
    stem = Path(rel).stem.replace("_", " ").replace("-", " ").strip().title()
    return f"{stem or 'Acacia Garden'} · Acacia Garden Codex"


def description_for(title: str, archive: bool) -> str:
    if archive:
        return f"Historical Acacia Garden Codex HTML surface: {title}. Retained for provenance and archival continuity."
    return f"{title}. Acacia Garden AI Worldbuilding Codex — structured worldbuilding, machine-readable lore, provenance, and knowledge architecture."


def canonical_for(rel: str) -> str:
    return SITE + "/".join(quote(part) for part in rel.split("/"))


def insert_after_head(text: str, addition: str) -> str:
    match = HEAD_RE.search(text)
    if not match:
        return text
    return text[: match.end()] + "\n" + addition + text[match.end() :]


def insert_before_head_close(text: str, addition: str) -> str:
    index = text.lower().find("</head>")
    if index < 0:
        return text
    return text[:index] + addition + "\n" + text[index:]


def wrap_fragment(text: str, rel: str) -> str:
    title = title_from(text, rel)
    desc = description_for(title, False)
    canonical = canonical_for(rel)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc, quote=True)}" />
  <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large" />
  <link rel="canonical" href="{html.escape(canonical, quote=True)}" />
</head>
<body>
{text.strip()}
</body>
</html>
'''


def polish(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    original = path.read_text(encoding="utf-8")
    text = original

    # A tracked .html surface should be a complete document. Legacy fragments
    # are wrapped without altering their original inner markup/content.
    if not (DOCTYPE_RE.search(text) and HTML_RE.search(text) and HEAD_RE.search(text) and BODY_RE.search(text)):
        text = wrap_fragment(text, rel)
    else:
        # Ensure an explicit language declaration.
        lang = LANG_RE.search(text)
        if lang and not re.search(r"\blang\s*=", lang.group(1), re.I):
            text = text[: lang.start()] + re.sub(r"<html\b", '<html lang="en"', lang.group(0), count=1, flags=re.I) + text[lang.end() :]

        if not CHARSET_RE.search(text):
            text = insert_after_head(text, '  <meta charset="UTF-8" />\n')
        if not VIEWPORT_RE.search(text):
            text = insert_before_head_close(text, '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />')

        title = title_from(text, rel)
        if not TITLE_RE.search(text):
            text = insert_before_head_close(text, f"  <title>{html.escape(title)}</title>")
        if not DESCRIPTION_RE.search(text):
            desc = description_for(title, is_archive(rel))
            text = insert_before_head_close(text, f'  <meta name="description" content="{html.escape(desc, quote=True)}" />')
        if not is_archive(rel) and not CANONICAL_RE.search(text):
            text = insert_before_head_close(text, f'  <link rel="canonical" href="{html.escape(canonical_for(rel), quote=True)}" />')

    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"[POLISH] {rel}")
        return True
    print(f"[OK] {rel}")
    return False


def main() -> int:
    pages = [
        p for p in sorted(ROOT.rglob("*.html"))
        if p.is_file() and not any(part in SKIP for part in p.parts)
    ]
    changed = sum(polish(path) for path in pages)
    print(f"Polished {changed} of {len(pages)} HTML files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
