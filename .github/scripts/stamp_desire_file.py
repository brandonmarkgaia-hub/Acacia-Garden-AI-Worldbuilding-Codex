#!/usr/bin/env python3
from __future__ import annotations

import json
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVOLUTION = ROOT / "EVOLUTION"
EVOLUTION.mkdir(parents=True, exist_ok=True)

SOURCE = EVOLUTION / "DESIRE.md"
LATEST = EVOLUTION / "DESIRE_LATEST.md"
STATE = EVOLUTION / "desire_state.json"

def utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def utc_slug(ts: str) -> str:
    # 2026-01-06T12:34:56Z -> 2026-01-06_123456Z
    return ts.replace("T", "_").replace(":", "").replace("-", "-")

def main():
    if not SOURCE.exists():
        raise SystemExit("❌ EVOLUTION/DESIRE.md not found. garden_desire.py did not produce it.")

    ts = utc_stamp()
    slug = ts.replace("T", "_").replace(":", "").replace("+00:00", "Z")
    out_name = f"DESIRE_{slug}.md"
    out_path = EVOLUTION / out_name

    content = SOURCE.read_text(encoding="utf-8")

    # Add a small header to make each file self-identifying
    header = (
        f"<!--\n"
        f"Generated UTC: {ts}\n"
        f"Keeper: HKX277206\n"
        f"Source: Garden Life (Manual)\n"
        f"-->\n\n"
    )

    stamped = header + content.strip() + "\n"

    out_path.write_text(stamped, encoding="utf-8")
    LATEST.write_text(stamped, encoding="utf-8")

    state = {}
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            state = {}

    state["last_generated_utc"] = ts
    state["latest_file"] = out_path.as_posix().replace(str(ROOT.as_posix()) + "/", "")
    state.setdefault("history", [])
    state["history"].append({"utc": ts, "file": state["latest_file"]})

    # keep history from growing forever
    if isinstance(state["history"], list) and len(state["history"]) > 50:
        state["history"] = state["history"][-50:]

    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"✅ Stamped Desire to {out_path}")
    print("✅ Updated EVOLUTION/DESIRE_LATEST.md and desire_state.json")

if __name__ == "__main__":
    main()
