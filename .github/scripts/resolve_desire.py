#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVOLUTION = ROOT / "EVOLUTION"
RESOLVED = EVOLUTION / "RESOLVED"
STATE = EVOLUTION / "desire_state.json"

def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="Path to the Desire md file (e.g. EVOLUTION/DESIRE_...md)")
    ap.add_argument("--note", required=True, help="Short resolution note")
    args = ap.parse_args()

    src = (ROOT / args.file).resolve()
    if not src.exists():
        raise SystemExit(f"Missing file: {args.file}")

    RESOLVED.mkdir(parents=True, exist_ok=True)

    ts = utc_now_iso()
    dst = RESOLVED / src.name

    content = src.read_text(encoding="utf-8", errors="ignore").strip()
    header = (
        f"\n\n---\n"
        f"## ✅ Resolved\n"
        f"- Resolved UTC: {ts}\n"
        f"- Note: {args.note}\n"
    )
    dst.write_text(content + header + "\n", encoding="utf-8")

    # Keep original (optional). If you want move instead of copy, uncomment move.
    # src.unlink(missing_ok=True)
    # For safety, we keep original and also write resolved copy:
    print(f"✅ Wrote resolved copy: {dst.as_posix()}")

    # Update desire_state.json
    state = {}
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            state = {}

    state.setdefault("resolved", [])
    state["resolved"].append({"utc": ts, "file": f"EVOLUTION/RESOLVED/{dst.name}", "note": args.note})
    if len(state["resolved"]) > 100:
        state["resolved"] = state["resolved"][-100:]

    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("✅ Updated EVOLUTION/desire_state.json")

if __name__ == "__main__":
    main()
