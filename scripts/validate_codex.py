#!/usr/bin/env python3
"""Acacia Garden Gatekeeper.

Repository-wide integrity checks for current state and every tracked HTML file.
The validator deliberately separates structural validity from canon/authority:
it verifies transport, links, metadata, indexes, and machine readability without
promoting historical or generated material into current canon.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

ROOT_DIR = Path(__file__).resolve().parent.parent
STATUS_PATH = ROOT_DIR / "STATUS.json"
PATH_SECTIONS = ("chambers", "blooms", "echoes", "vaults", "orchards")
PROJECT_PREFIX = "/Acacia-Garden-AI-Worldbuilding-Codex/"
SITE_ORIGIN = "brandonmarkgaia-hub.github.io"
HTML_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "_site"}
ARCHIVE_PREFIXES = ("docs/Archives/", "_ROOT_ARCHIVE/")
RETIRED_CURRENT_PATTERNS = (
    "CODEX_MONOLITH_CHUNK_",
    "docs/Archives/CODEX_MONOLITH.html",
)
HTML_ATTR_RE = re.compile(r"(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.I)
DOCTYPE_RE = re.compile(r"<!doctype\s+html\s*>", re.I)
META_CHARSET_RE = re.compile(r"<meta\b[^>]*charset\s*=\s*[\"']?utf-8", re.I)
VIEWPORT_RE = re.compile(r"<meta\b[^>]*name\s*=\s*[\"']viewport[\"']", re.I)
DESCRIPTION_RE = re.compile(r"<meta\b[^>]*name\s*=\s*[\"']description[\"']", re.I)
CANONICAL_RE = re.compile(r"<link\b[^>]*rel\s*=\s*[\"'][^\"']*canonical", re.I)
ROBOTS_NOINDEX_RE = re.compile(r"<meta\b[^>]*name\s*=\s*[\"']robots[\"'][^>]*content\s*=\s*[\"'][^\"']*noindex", re.I)
JSONLD_RE = re.compile(
    r"<script\b[^>]*type\s*=\s*[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.I | re.S,
)


class GardenHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: dict[str, int] = {}
        self.ids: list[str] = []
        self.html_lang = ""
        self.title_text: list[str] = []
        self._in_title = False
        self.parse_errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self.tags[tag] = self.tags.get(tag, 0) + 1
        data = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.html_lang = data.get("lang", "").strip()
        if tag == "title":
            self._in_title = True
        if data.get("id"):
            self.ids.append(data["id"])

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_text.append(data)

    def error(self, message: str) -> None:  # pragma: no cover - compatibility hook
        self.parse_errors.append(message)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object, got {type(data).__name__}")
    return data


def extract_path(item: Any) -> tuple[str | None, str]:
    if isinstance(item, str):
        value = item.strip()
        return (value or None, item)
    if isinstance(item, dict):
        raw = item.get("path")
        value = raw.strip() if isinstance(raw, str) else ""
        return (value or None, str(item.get("id") or value or "<object entry>"))
    return (None, repr(item))


def resolve_repo_path(path: str) -> Path | None:
    candidate = (ROOT_DIR / path).resolve()
    try:
        candidate.relative_to(ROOT_DIR)
    except ValueError:
        return None
    return candidate


def validate_status_paths(status: dict[str, Any]) -> tuple[int, int]:
    errors = 0
    checked = 0
    for section_name in PATH_SECTIONS:
        items = status.get(section_name, [])
        if not isinstance(items, list):
            print(f"[ERROR] {section_name}: expected list, got {type(items).__name__}")
            errors += 1
            continue
        section_errors = 0
        for item in items:
            path, label = extract_path(item)
            if not path:
                print(f"[ERROR] {section_name}: entry has no valid path: {label}")
                errors += 1
                section_errors += 1
                continue
            full = resolve_repo_path(path)
            checked += 1
            if full is None:
                print(f"[ERROR] {section_name}: path escapes repository root: {path}")
                errors += 1
                section_errors += 1
            elif not full.exists():
                print(f"[ERROR] {section_name}: path not found: {path}")
                errors += 1
                section_errors += 1
        print(f"[Gatekeeper] {section_name}: checked {len(items)}, errors {section_errors}")
    return errors, checked


def html_files() -> list[Path]:
    result: list[Path] = []
    for path in sorted(ROOT_DIR.rglob("*.html")):
        if path.is_file() and not any(part in HTML_SKIP_DIRS for part in path.parts):
            result.append(path)
    return result


def is_archive(rel: str) -> bool:
    return any(rel.startswith(prefix) for prefix in ARCHIVE_PREFIXES)


def read_html(path: Path) -> str:
    # strict UTF-8 is intentional: silent replacement hides damaged documents.
    return path.read_text(encoding="utf-8")


def resolve_local_target(page: Path, raw_target: str) -> Path | None:
    target = raw_target.strip()
    if not target or target.startswith("#"):
        return None
    if target.startswith(("//", "data:", "mailto:", "tel:", "javascript:")):
        return None

    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme in {"http", "https"} and parsed.netloc.lower() == SITE_ORIGIN and parsed.path.startswith(PROJECT_PREFIX):
            path_text = unquote(parsed.path)
        else:
            return None
    else:
        path_text = unquote(parsed.path)
    if not path_text:
        return None

    if path_text.startswith(PROJECT_PREFIX):
        candidate = ROOT_DIR / path_text[len(PROJECT_PREFIX):]
    elif path_text.startswith("/"):
        return None
    else:
        candidate = page.parent / path_text

    candidate = candidate.resolve()
    try:
        candidate.relative_to(ROOT_DIR)
    except ValueError:
        return (ROOT_DIR.parent / "__outside_project__" / "escape").resolve()
    if path_text.endswith("/"):
        candidate = candidate / "index.html"
    return candidate


def validate_html_structure() -> tuple[int, int]:
    errors = 0
    pages = html_files()
    for page in pages:
        rel = page.relative_to(ROOT_DIR).as_posix()
        try:
            text = read_html(page)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"[ERROR] html-structure: unreadable UTF-8: {rel}: {exc}")
            errors += 1
            continue

        parser = GardenHTMLParser()
        try:
            parser.feed(text)
            parser.close()
        except Exception as exc:
            print(f"[ERROR] html-structure: parser failure: {rel}: {exc}")
            errors += 1
            continue

        required = {
            "doctype": bool(DOCTYPE_RE.search(text)),
            "html": parser.tags.get("html", 0) == 1,
            "lang": bool(parser.html_lang),
            "head": parser.tags.get("head", 0) == 1,
            "body": parser.tags.get("body", 0) == 1,
            "title": parser.tags.get("title", 0) == 1 and bool("".join(parser.title_text).strip()),
            "charset": bool(META_CHARSET_RE.search(text)),
            "viewport": bool(VIEWPORT_RE.search(text)),
        }
        for label, ok in required.items():
            if not ok:
                print(f"[ERROR] html-structure: {rel}: missing/invalid {label}")
                errors += 1

        duplicates = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
        for duplicate in duplicates:
            print(f"[ERROR] html-structure: {rel}: duplicate id={duplicate!r}")
            errors += 1

        for payload in JSONLD_RE.findall(text):
            try:
                json.loads(payload)
            except json.JSONDecodeError as exc:
                print(f"[ERROR] html-structure: {rel}: invalid JSON-LD: {exc}")
                errors += 1

        # Current public pages should be search-machine legible. Historical HTML
        # may instead declare noindex; it still must be a complete HTML document.
        if not is_archive(rel):
            if not DESCRIPTION_RE.search(text):
                print(f"[ERROR] html-metadata: {rel}: missing meta description")
                errors += 1
            if not CANONICAL_RE.search(text):
                print(f"[ERROR] html-metadata: {rel}: missing canonical link")
                errors += 1
        elif not (DESCRIPTION_RE.search(text) or ROBOTS_NOINDEX_RE.search(text)):
            print(f"[ERROR] html-metadata: {rel}: historical page needs description or robots=noindex")
            errors += 1

        if not is_archive(rel):
            for stale in RETIRED_CURRENT_PATTERNS:
                if stale in text:
                    print(f"[ERROR] html-stale: {rel}: current page references retired surface {stale}")
                    errors += 1

    print(f"[Gatekeeper] HTML structure/metadata: checked {len(pages)} page(s), errors {errors}")
    return errors, len(pages)


def validate_html_links() -> tuple[int, int]:
    errors = 0
    checked = 0
    seen: set[tuple[str, str]] = set()
    for page in html_files():
        rel_page = page.relative_to(ROOT_DIR).as_posix()
        try:
            text = read_html(page)
        except (OSError, UnicodeDecodeError):
            continue
        for raw in HTML_ATTR_RE.findall(text):
            target = resolve_local_target(page, raw)
            if target is None:
                continue
            checked += 1
            try:
                target.relative_to(ROOT_DIR)
            except ValueError:
                key = (rel_page, raw)
                if key not in seen:
                    print(f"[ERROR] html-link: target leaves project: {rel_page} -> {raw}")
                    seen.add(key)
                    errors += 1
                continue
            if target.is_dir() and (target / "index.html").exists():
                continue
            if target.exists():
                continue
            key = (rel_page, raw)
            if key not in seen:
                try:
                    rel_target = target.relative_to(ROOT_DIR).as_posix()
                except ValueError:
                    rel_target = raw
                print(f"[ERROR] html-link: missing local target: {rel_page} -> {raw} ({rel_target})")
                seen.add(key)
                errors += 1
    print(f"[Gatekeeper] HTML links/assets: checked {checked}, errors {errors}")
    return errors, checked


def validate_machine_surfaces() -> tuple[int, int]:
    errors = 0
    checked = 0
    json_surfaces = (
        "AUTHORITY.json",
        "STATUS.json",
        "machine-index.json",
        "machine-discovery.json",
        ".well-known/acacia.json",
        "docs/Archives/GARDEN_MANIFEST.json",
        "docs/Archives/FULL_CODEX_INDEX.json",
        "docs/api/GARDEN_API_INDEX.json",
        "docs/docs_urls.json",
    )
    text_surfaces = ("README.md", "DISCOVERY.md", "llms.txt", "llms-full.txt", "AGENTS.md", "robots.txt", "sitemap.xml")
    for rel in json_surfaces:
        checked += 1
        path = ROOT_DIR / rel
        if not path.exists():
            print(f"[ERROR] machine: missing required surface: {rel}")
            errors += 1
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"[ERROR] machine: invalid JSON surface {rel}: {exc}")
            errors += 1
    for rel in text_surfaces:
        checked += 1
        path = ROOT_DIR / rel
        if not path.exists() or path.stat().st_size == 0:
            print(f"[ERROR] machine: missing/empty required surface: {rel}")
            errors += 1
    print(f"[Gatekeeper] Machine surfaces: checked {checked}, errors {errors}")
    return errors, checked


def main() -> int:
    if not STATUS_PATH.exists():
        print(f"[ERROR] STATUS.json not found at {STATUS_PATH}")
        return 1
    try:
        status = load_json(STATUS_PATH)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"[ERROR] Failed to load STATUS.json: {exc}")
        return 1

    print("[Gatekeeper] Full Director integrity audit")
    status_errors, status_checked = validate_status_paths(status)
    structure_errors, structure_checked = validate_html_structure()
    link_errors, link_checked = validate_html_links()
    machine_errors, machine_checked = validate_machine_surfaces()

    errors = status_errors + structure_errors + link_errors + machine_errors
    checked = status_checked + structure_checked + link_checked + machine_checked
    if errors:
        print(f"[Gatekeeper] Validation failed: {errors} error(s) across {checked} checked item(s).")
        return 1
    print(f"[Gatekeeper] Validation passed: {checked} checked item(s) verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
