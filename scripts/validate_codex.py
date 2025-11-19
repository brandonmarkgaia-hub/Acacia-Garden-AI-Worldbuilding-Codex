import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS_FILE = os.path.join(ROOT, "STATUS.json")

print("🔍 Running Codex validation...")

try:
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        status = json.load(f)
except Exception as e:
    print("❌ ERROR: Failed to load STATUS.json:", e)
    sys.exit(1)

# For now, just check that 'structures' exists and is a dict
structures = status.get("structures")
if not isinstance(structures, dict):
    print("❌ ERROR: STATUS.json is missing a valid 'structures' object.")
    sys.exit(1)

print("✅ Codex validation successful.")
