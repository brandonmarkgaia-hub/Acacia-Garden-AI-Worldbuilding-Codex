#!/usr/bin/env python3
"""
Garden Codex Validator (Gatekeeper)
Checks structural integrity of the Codex.

- Verifies STATUS.json exists and is well-formed.
- Verifies that each declared path in STATUS.json exists.
- If garden_scan_report.json is present, cross-checks:
    - Echo files have echo_header hits.
    - Chamber files have chamber_word hits.

Exit codes:
    0 = OK (no errors, warnings allowed)
    1 = Errors detected (missing files or critical issues)
"""

import os
import sys
import json
from typing import Dict, Any

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATUS_PATH = os.path.join(ROOT_DIR, "STATUS.json")
SCAN_PATH = os.path.join(ROOT_DIR, "garden_scan_report.json")


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_status_paths(status: Dict[str, Any]) -> int:
def validate_status_paths(status: Dict[str, Any]) -> int:
    errors = 0

    def check_section(section_name: str):
        nonlocal errors
        items = status.get(section_name, [])

        # We only validate list-based sections. 'structures' is an object, so skip it.
        if not isinstance(items, list):
            print(
                f"[Gatekeeper] Skipping section '{section_name}': "
                f"expected list, got {type(items).__name__}"
            )
            return

        for item in items:
            if not isinstance(item, dict):
                print(
                    f"[Gatekeeper] Skipping non-object entry in '{section_name}': {item!r}"
                )
                continue

            path = item.get("path", "").strip()
            if not path:
                print(f"[WARN] {section_name} entry {item.get('id')} has no path defined.")
                continue

            full = os.path.join(ROOT_DIR, path)
            if not os.path.exists(full):
                print(
                    f"[ERROR] {section_name} entry {item.get('id')} path not found: {path}"
                )
                errors += 1

    # Only check the list-based sections
    for section in ("chambers", "blooms", "echoes", "vaults", "orchards"):
        check_section(section)

    return errors


def cross_check_with_scan(status: Dict[str, Any], scan: Dict[str, Any]) -> int:
    errors = 0
    warnings = 0
    scan_files = scan.get("files", {})

    # Echoes: ensure file is scanned and has echo_header matches
    for echo in status.get("echoes", []):
        path = echo.get("path", "").strip()
        if not path:
            continue
        f_info = scan_files.get(path)
        if not f_info:
            print(f"[WARN] Echo {echo.get('id')} file not in scanner index: {path}")
            warnings += 1
            continue
        matches = f_info.get("matches", {})
        if "echo_header" not in matches:
            print(f"[WARN] Echo {echo.get('id')} has no echo_header hits in scan: {path}")
            warnings += 1

    # Chambers: ensure file has chamber_word hits if present
    for chamber in status.get("chambers", []):
        path = chamber.get("path", "").strip()
        if not path:
            continue
        f_info = scan_files.get(path)
        if not f_info:
            print(f"[WARN] Chamber {chamber.get('id')} file not in scanner index: {path}")
            warnings += 1
            continue
        matches = f_info.get("matches", {})
        if "chamber_word" not in matches:
            print(f"[WARN] Chamber {chamber.get('id')} has no 'chamber' word hits in scan: {path}")
            warnings += 1

    # Only warnings here; no hard errors
    return errors


def main() -> int:
    if not os.path.exists(STATUS_PATH):
        print(f"[ERROR] STATUS.json not found at {STATUS_PATH}")
        return 1

    try:
        status = load_json(STATUS_PATH)
    except Exception as e:
        print(f"[ERROR] Failed to load STATUS.json: {e}")
        return 1

    print("[Gatekeeper] STATUS.json loaded.")

    errors = 0

    # 1) Validate paths from STATUS.json
    print("[Gatekeeper] Validating STATUS paths...")
    errors += validate_status_paths(status)

    # 2) Optional cross-check with garden_scan_report.json
    if os.path.exists(SCAN_PATH):
        try:
            scan = load_json(SCAN_PATH)
            print("[Gatekeeper] garden_scan_report.json loaded. Cross-checking...")
            errors += cross_check_with_scan(status, scan)
        except Exception as e:
            print(f"[WARN] Failed to load garden_scan_report.json: {e}")
    else:
        print("[Gatekeeper] garden_scan_report.json not found; skipping scan cross-check.")

    if errors > 0:
        print(f"[Gatekeeper] Validation finished with {errors} error(s).")
        return 1

    print("[Gatekeeper] Validation finished. No errors detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
