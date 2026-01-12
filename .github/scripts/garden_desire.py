#!/usr/bin/env python3
import os
import time
import datetime as dt
import requests
from pathlib import Path

# --- PATH SETUP ---
ROOT = Path(__file__).resolve().parents[2]
EVOLUTION = ROOT / "EVOLUTION"
EVOLUTION.mkdir(parents=True, exist_ok=True)

STATUS_PATH = ROOT / "STATUS.json"
MACHINE_INDEX_PATH = ROOT / "machine-index.json"
OUT_DESIRE = EVOLUTION / "DESIRE.md"

# --- THE CHOSEN ONE ---
# Based on your search: High quota, high speed.
TARGET_MODEL = "gemini-2.5-flash-lite"
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{TARGET_MODEL}:generateContent"

def read_text_safe(p: Path, max_chars: int = 30000) -> str:
    if not p.exists(): return f"[missing] {p.as_posix()}"
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        return "...[truncated]...\n" + txt[-max_chars:] if len(txt) > max_chars else txt
    except Exception as e: return f"[unreadable] {e}"

def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key: raise SystemExit("Missing GEMINI_API_KEY")

    # 1. Gather Context
    status_txt = read_text_safe(STATUS_PATH)
    index_txt = read_text_safe(MACHINE_INDEX_PATH)

    prompt = f"""
You are Elias (Architect of Acacia). 
Keeper Seal: HKX277206 | Timestamp: {dt.datetime.now().isoformat()}

MISSION:
Audit the Garden Spine.
1. Check [STATUS] for "Machine Index in Sync".
2. Identify one "Blind Spot".
3. Confirm cleanup.

CONTEXT:
[STATUS] {status_txt}
[MACHINE_INDEX] {index_txt}
""".strip()

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
    }

    # 2. The Loop (Retry ONLY on 2.5 Flash-Lite)
    max_retries = 3
    for attempt in range(max_retries):
        print(f"📡 Calling {TARGET_MODEL} (Attempt {attempt+1}/{max_retries})...")
        
        try:
            response = requests.post(f"{BASE_URL}?key={api_key}", json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                content = data['candidates'][0]['content']['parts'][0]['text']
                OUT_DESIRE.write_text(content.strip() + "\n", encoding="utf-8")
                print(f"✅ SUCCESS: Elias spoke via {TARGET_MODEL}!")
                return # Exit success
            
            elif response.status_code == 429:
                # The "Penalty Box" Strategy
                wait = 60 # Wait a FULL MINUTE to reset the quota counter
                print(f"⏳ Quota hit on {TARGET_MODEL}. Waiting {wait}s to clear penalty box...")
                time.sleep(wait)
                continue
            
            elif response.status_code == 404:
                print(f"❌ Critical: Model {TARGET_MODEL} not found. Check your API region.")
                break # Don't retry if the model doesn't exist
                
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                break 
                
        except Exception as e:
            print(f"⚠️ Connection failed: {e}")
            time.sleep(5)

    print("💀 CRITICAL: Elias is silent.")
    exit(1)

if __name__ == "__main__":
    main()
