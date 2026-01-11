#!/usr/bin/env python3
from __future__ import annotations

import os
import json
import argparse
import datetime as dt
from pathlib import Path
from google import genai 

# Path Setup
ROOT = Path(__file__).resolve().parents[2]
EVOLUTION = ROOT / "EVOLUTION"
EVOLUTION.mkdir(parents=True, exist_ok=True)

STATUS_PATH = ROOT / "STATUS.json"
MACHINE_INDEX_PATH = ROOT / "machine-index.json"
SCAN_REPORT_PATH = ROOT / "tools" / "garden_scan_report.json"
OUT_DESIRE = EVOLUTION / "DESIRE.md"

def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def read_text_safe(p: Path, max_chars: int = 35000) -> str:
    """Squeezes context to prevent 429 quota exhaustion"""
    if not p.exists(): return f"[missing] {p.as_posix()}"
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        return "...[truncated]...\n" + txt[-max_chars:] if len(txt) > max_chars else txt
    except Exception as e: return f"[unreadable] {e}"

def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key: raise SystemExit("Missing GEMINI_API_KEY")

    # Use v1beta to ensure the gemini-1.5-flash model is found
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    
    prompt = f"""
You are Elias (Architect). 
Keeper Seal: HKX277206 | Timestamp: {utc_now_iso()}

MISSION:
Audit the 1,525-node Spine for navigation health and AI-readability. 
Search for lore gaps in the 798 Chambers and 178 Echoes.

CONTEXT:
[STATUS] {read_text_safe(STATUS_PATH)}
[MACHINE_INDEX] {read_text_safe(MACHINE_INDEX_PATH)}
[SCAN_REPORT] {read_text_safe(SCAN_REPORT_PATH)}
""".strip()

    # Model call using the verified alias
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents=prompt
    )

    if response.text:
        OUT_DESIRE.write_text(response.text.strip() + "\n", encoding="utf-8")
        print(f"✅ Success: Elias (Architect) has synchronized with the 1,525-node Garden.")

if __name__ == "__main__":
    main()
