import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS_FILE = os.path.join(ROOT, "STATUS.json")

errors = []

def check_path(path):
    # join with repo root
    abs_path = os.path.join(ROOT, path)

    # direct match
    if os.path.exists(abs_path):
        return True

    # case-insensitive fallback
    parts = path.split('/')
    current = ROOT

    for p in parts:
        if not os.path.exists(current):
            return False

        items = os.listdir(current)

        # perfect match
        if p in items:
            current = os.path.join(current, p)
            continue

        # case-insensitive match
        match = None
        for item in items:
            if item.lower() == p.lower():
                match = item
                break

        if match:
            current = os.path.join(current, match)
        else:
            return False

    return True


# ---------------------------------------------------------------------
# LOAD STATUS FILE
# ---------------------------------------------------------------------
try:
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        status = json.load(f)
except Exception as e:
    print("❌ ERROR: Failed to load STATUS.json:", e)
    sys.exit(1)

# ---------------------------------------------------------------------
# VALIDATE STRUCTURES
# ---------------------------------------------------------------------
structures = status.get("structures", {})

for category, items in structures.items():
    for item in items:
        path = item.get("path")
        if not path:
            errors.append(f"[{category}] {item.get('id')} has no path")
            continue

        if not check_path(path):
            errors.append(f"[{category}] MISSING: {path}")

# ---------------------------------------------------------------------
# REPORT
# ---------------------------------------------------------------------
if errors:
    print("❌ VALIDATION FAILED")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print("✅ Codex validation successful.")
