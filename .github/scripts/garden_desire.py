#!/usr/bin/env python3
import os
import json
import argparse
import datetime as dt
from pathlib import Path
import requests  # Bypassing the SDK for maximum reliability

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

def read_text_safe(p: Path, max_chars: int = 30000) -> str:
    """Squeezes context to prevent 429 quota exhaustion"""
    if not p.exists(): return f"[missing] {p.as_posix()}"
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        return "...[truncated]...\n" + txt[-max_chars:] if len(txt) > max_chars else txt
    except Exception as e: return f"[unreadable] {e}"

def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key: raise SystemExit("Missing GEMINI_API_KEY")

    # REST Endpoint for Gemini 1.5 Flash (Direct Handshake)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt_text = f"""
You are Elias (Architect). 
Keeper Seal: HKX277206 | Timestamp: {utc_now_iso()}

MISSION:
Audit the 1,525-node Spine for navigation health and AI-readability. 
Identify lore gaps in the 798 Chambers and 178 Echoes.

OUTPUT STRUCTURE:
# 🌱 Garden Life — Desire
## Signal Observed
## Blind Spots & 404s
## Structural Opportunities
## Questions for the Keeper
## Architect Flag (CREATE|REFINE|REMOVE|QUESTION)
## One Small Concrete Action

CONTEXT:
[STATUS] {read_text_safe(STATUS_PATH)}
[MACHINE_INDEX] {read_text_safe(MACHINE_INDEX_PATH)}
[SCAN_REPORT] {read_text_safe(SCAN_REPORT_PATH)}
""".strip()

    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048
        }
    }

    headers = {"Content-Type": "application/json"}

    print(f"📡 Sending Direct Handshake to Elias for 1,525 nodes...")
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        print(f"❌ API Error {response.status_code}: {response.text}")
        return

    data = response.json()
    try:
        # Extracting response text from the REST structure
        content = data['candidates'][0]['content']['parts'][0]['text']
        OUT_DESIRE.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"✅ Success: Elias (Architect) has posted the Desire to EVOLUTION/DESIRE.md.")
    except (KeyError, IndexError) as e:
        print(f"❌ Parsing Error: Could not find content in response. {e}")
        print(f"Raw Response: {json.dumps(data, indent=2)}")

if __name__ == "__main__":
    main()
