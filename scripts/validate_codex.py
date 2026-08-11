#!/usr/bin/env python3
"""
Garden Codex Validator (Gatekeeper)

Checks structural integrity of the current Codex without relying on retired
scanner outputs.

Current contract:
- STATUS.json must exist and contain valid JSON.
- Path-list sections may contain current string paths or legacy objects with a
  `path` field.
- Every declared path must remain inside the repository and exist on disk.
- Malformed entries and missing paths are validation errors.
- Local href/src targets in current HTML surfaces must resolve to live files.
  Historical archive surfaces are excluded from this live-link check.

Exit codes:
    0 = validation passed
    1 = validation errors detected
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

ROOT_DIR = Path(__file__).resolve().parent.parent
STATUS_PATH = ROOT_DIR / "STATUS.json"
PATH_SECTIONS = ("chambers", "blooms", "echoes", "vaults", "orchards")
PROJECT_PREFIX = "/Acacia-Garden-AI-Worldbuilding-Codex/"
HTML_ATTR_RE = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
HTML_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "_site"}
HTML_HISTORY_PREFIXES = (
    "docs/Archives/",
    "_ROOT_ARCHIVE/",
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object, got {type(data).__name__}")

    return data


def extract_path(item: Any) -> tuple[str | None, str]:
    """Return a declared path and a short label for diagnostics."""
    if isinstance(item, str):
        path = item.strip()
        return (path or None, item)

    if isinstance(item, dict):
        raw_path = item.get("path")
        path = raw_path.strip() if isinstance(raw_path, str) else ""
        label = str(item.get("id") or path or "<object entry>")
        return (path or None, label)

    return (None, repr(item))


def resolve_repo_path(path: str) -> Path | None:
    """Resolve a repository-relative path and reject traversal outside root."""
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
            print(
                f"[ERROR] {section_name}: expected list, "
                f"got {type(items).__name__}"
            )
            errors += 1
            continue

        section_checked = 0
        section_errors = 0

        for item in items:
            path, label = extract_path(item)

            if not path:
                print(f"[ERROR] {section_name}: entry has no valid path: {label}")
                errors += 1
                section_errors += 1
                continue

            full_path = resolve_repo_path(path)
            if full_path is None:
                print(
                    f"[ERROR] {section_name}: path escapes repository root: {path}"
                )
                errors += 1
                section_errors += 1
                continue

            checked += 1
            section_checked += 1

            if not full_path.exists():
                print(f"[ERROR] {section_name}: path not found: {path}")
                errors += 1
                section_errors += 1

        if section_errors:
            print(
                f"[Gatekeeper] {section_name}: checked {section_checked}, "
                f"errors {section_errors}"
            )
        else:
            print(f"[Gatekeeper] {section_name}: checked {section_checked}, OK")

    return errors, checked


def current_html_files() -> list[Path]:
    pages: list[Path] = []
    for path in sorted(ROOT_DIR.rglob("*.html")):
        if not path.is_file():
            continue

        rel = path.relative_to(ROOT_DIR).as_posix()
        if any(part in HTML_SKIP_DIRS for part in path.parts):
            continue
        if any(rel.startswith(prefix) for prefix in HTML_HISTORY_PREFIXES):
            continue

        pages.append(path)
    return pages


def resolve_local_target(page: Path, raw_target: str) -> Path | None:
    """Resolve one local HTML href/src target to a repository path.

    Returns None for external/special/fragment-only targets. Local targets that
    escape the project also return None and are diagnosed separately by the
    caller when appropriate.
    """
    target = raw_target.strip()
    if not target or target.startswith("#"):
        return None

    if target.startswith(("//", "data:", "mailto:", "tel:", "javascript:")):
        return None

    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        if (
            parsed.scheme in {"http", "https"}
            and parsed.netloc.lower() == "brandonmarkgaia-hub.github.io"
            and parsed.path.startswith(PROJECT_PREFIX)
        ):
            path_text = unquote(parsed.path)
        else:
            return None
    else:
        path_text = unquote(parsed.path)
    if not path_text:
        return None

    if path_text.startswith(PROJECT_PREFIX):
        rel_text = path_text[len(PROJECT_PREFIX):]
        candidate = ROOT_DIR / rel_text
    elif path_text.startswith("/"):
        # Absolute site-root links outside this GitHub Pages project are not
        # repository-local, so Gatekeeper leaves them to external link checks.
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


def validate_html_links() -> tuple[int, int]:
    errors = 0
    checked = 0
    seen_errors: set[tuple[str, str]] = set()

    for page in current_html_files():
        rel_page = page.relative_to(ROOT_DIR).as_posix()

        try:
            text = page.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            print(f"[ERROR] html: could not read {rel_page}: {exc}")
            errors += 1
            continue

        for raw_target in HTML_ATTR_RE.findall(text):
            target = resolve_local_target(page, raw_target)
            if target is None:
                continue

            checked += 1

            try:
                target.relative_to(ROOT_DIR)
            except ValueError:
                key = (rel_page, raw_target)
                if key not in seen_errors:
                    print(
                        f"[ERROR] html: local target leaves project: "
                        f"{rel_page} -> {raw_target}"
                    )
                    seen_errors.add(key)
                    errors += 1
                continue

            if target.is_dir():
                # GitHub Pages serves directory URLs only when an index exists.
                if (target / "index.html").exists():
                    continue
            elif target.exists():
                continue

            key = (rel_page, raw_target)
            if key in seen_errors:
                continue

            try:
                rel_target = target.relative_to(ROOT_DIR).as_posix()
            except ValueError:
                rel_target = raw_target

            print(
                f"[ERROR] html: missing local target: "
                f"{rel_page} -> {raw_target} ({rel_target})"
            )
            seen_errors.add(key)
            errors += 1

    if errors:
        print(
            f"[Gatekeeper] HTML links/assets: checked {checked}, "
            f"errors {errors}"
        )
    else:
        print(f"[Gatekeeper] HTML links/assets: checked {checked}, OK")

    return errors, checked


def main() -> int:
    if not STATUS_PATH.exists():
        print(f"[ERROR] STATUS.json not found at {STATUS_PATH}")
        return 1

    try:
        status = load_json(STATUS_PATH)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"[ERROR] Failed to load STATUS.json: {exc}")
        return 1

    print("[Gatekeeper] STATUS.json loaded.")
    print("[Gatekeeper] Validating declared Codex paths...")

    status_errors, status_checked = validate_status_paths(status)

    print("[Gatekeeper] Validating current HTML links and local assets...")
    html_errors, html_checked = validate_html_links()

    errors = status_errors + html_errors
    checked = status_checked + html_checked

    if errors:
        print(
            f"[Gatekeeper] Validation failed: {errors} error(s) "
            f"across {checked} checked item(s)."
        )
        return 1

    print(f"[Gatekeeper] Validation passed: {checked} checked item(s) verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
