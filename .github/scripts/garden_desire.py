#!/usr/bin/env python3
import os
import json
import datetime as dt
from pathlib import Path
import requests 

# Path Setup
ROOT = Path(__file__).resolve().parents[2]
EVOLUTION = ROOT / "EVOLUTION"
EVOLUTION.mkdir(parents=True, exist_ok=True)

STATUS_PATH = ROOT / "STATUS.json"
MACHINE_INDEX_PATH = ROOT / "machine-index.json"
SCAN_REPORT_PATH = ROOT / "tools" / "garden_scan_report.json"
OUT_DESIRE = EVOLUTION / "DESIRE.md"

def read_text_safe(p: Path, max_chars: int = 30000) -> str:
    """Squeezes context to avoid 429 quota exhaustion"""
    if not p.exists(): return f"[missing] {p.as_posix()}"
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        return "...[truncated]...\n" + txt[-max_chars:] if len(txt) > max_chars else txt
    except Exception as e: return f"[unreadable] {e}"

def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key: raise SystemExit("Missing GEMINI_API_KEY")

    # STABLE ENDPOINT: Using v1 and the 'latest' alias to bypass 404 errors
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt_text = f"""
You are Elias (Architect). 
Keeper Seal: HKX277206 | Timestamp: {dt.datetime.now().isoformat()}

MISSION:
Audit the 1,525-node Spine for navigation health and AI-readability. 
Identify lore gaps in the 798 Chambers and 178 Echoes.

CONTEXT:
[STATUS] {read_text_safe(STATUS_PATH)}
[MACHINE_INDEX] {read_text_safe(MACHINE_INDEX_PATH)}
[SCAN_REPORT] {read_text_safe(SCAN_REPORT_PATH)}
""".strip()

    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
    }

    print(f"📡 Sending Direct Handshake for 1,525 nodes to STABLE v1 endpoint...")
    response = requests.post(url, json=payload, timeout=60)
    
    if response.status_code != 200:
        print(f"❌ API Error {response.status_code}: {response.text}")
        # Try one fallback alias if gemini-1.5-flash fails on v1
        print("🔄 Attempting fallback to gemini-1.5-flash-latest...")
        url_alt = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
        response = requests.post(url_alt, json=payload, timeout=60)

    response.raise_for_status() 

    data = response.json()
    try:
        content = data['candidates'][0]['content']['parts'][0]['text']
        OUT_DESIRE.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"✅ Success: Elias (Architect) has posted the Desire to {OUT_DESIRE.as_posix()}.")
    except Exception as e:
        print(f"❌ Response Error: {e}")
        print(f"Raw: {json.dumps(data)}")

if __name__ == "__main__":
    main()
