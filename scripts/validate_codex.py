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

Exit codes:
    0 = validation passed
    1 = validation errors detected
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
STATUS_PATH = ROOT_DIR / "STATUS.json"
PATH_SECTIONS = ("chambers", "blooms", "echoes", "vaults", "orchards")


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

    errors, checked = validate_status_paths(status)

    if errors:
        print(
            f"[Gatekeeper] Validation failed: {errors} error(s) "
            f"across {checked} checked path(s)."
        )
        return 1

    print(f"[Gatekeeper] Validation passed: {checked} declared path(s) verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
