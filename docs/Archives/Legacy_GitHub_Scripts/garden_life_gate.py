#!/usr/bin/env python3
"""
garden_life_gate.py

Determines whether Garden Life (Elias) is allowed to generate a new Desire.

Rules:
- If STATUS.verification shows no outstanding violations, Desire is blocked.
- If growth.open is empty AND verification is fully green, Desire is blocked.
- Otherwise, Desire is allowed.

Outputs:
- allow_desire=true|false (GitHub Actions output)
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS_PATH = ROOT / "STATUS.json"


def main():
    status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))

    verification = status.get("verification", {})
    growth = status.get("growth", {})

    open_growth = growth.get("open", [])
    allow = False

    # Any archive violations?
    archives = verification.get("archives", {})
    if archives.get("missing_base_href", 0) > 0:
        allow = True

    # Navigation violations?
    navigation = verification.get("navigation", {})
    if navigation.get("verified") is False:
        allow = True

    # Explicit open growth items
    if isinstance(open_growth, list) and len(open_growth) > 0:
        allow = True

    # Final decision
    if allow:
        print("🌱 Desire generation ALLOWED (work remains).")
        print("allow_desire=true")
    else:
        print("🛑 Desire generation BLOCKED (Garden is verified green).")
        print("allow_desire=false")

    # GitHub Actions output
    with open(Path(".") / "allow_desire.out", "w") as f:
        f.write(f"allow_desire={'true' if allow else 'false'}\n")

    print(f"::set-output name=allow_desire::{str(allow).lower()}")


if __name__ == "__main__":
    main()
