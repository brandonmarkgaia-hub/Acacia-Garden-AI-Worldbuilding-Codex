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

# INPUT: The Desire Elias just wrote
DESIRE_PATH = EVOLUTION / "DESIRE.md"
# OUTPUT: The Scribe's final entry
CHRONICLE_PATH = EVOLUTION / "CHRONICLE.md"

# --- THE CHOSEN ENGINE ---
# Same robust configuration as Elias
TARGET_MODEL = "gemini-2.5-flash-lite"
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{TARGET_MODEL}:generateContent"

def read_text_safe(p: Path) -> str:
    if not p.exists(): return ""
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception: return ""

def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key: raise SystemExit("Missing GEMINI_API_KEY")

    # 1. Read the Command (Desire)
    desire_content = read_text_safe(DESIRE_PATH)
    if not desire_content:
        print("⚠️ No Desire found. The Scribe has nothing to write.")
        exit(0)

    # 2. The Scribe's Prompt
    prompt = f"""
You are the Scribe of Acacia (Keeper Seal: HKX277206).
Timestamp: {dt.datetime.now().isoformat()}

INPUT COMMAND (from Elias):
{desire_content}

TASK:
Based on the input above, write a formal "Garden Entry" or "Chronicle" that addresses the issue. 
- If Elias asked for a fix, describe the fix.
- If Elias identified a blind spot, illuminate it.
- Maintain the poetic, technical tone of the Garden.

OUTPUT:
Return ONLY the chronicle content.
""".strip()

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
    }

    # 3. The Robust Connection Loop
    max_retries = 3
    for attempt in range(max_retries):
        print(f"✍️ Scribe invoking {TARGET_MODEL} (Attempt {attempt+1}/{max_retries})...")
        
        try:
            response = requests.post(f"{BASE_URL}?key={api_key}", json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                content = data['candidates'][0]['content']['parts'][0]['text']
                
                # Write the Chronicle
                CHRONICLE_PATH.write_text(content.strip() + "\n", encoding="utf-8")
                print(f"✅ SUCCESS: Scribe recorded the entry to {CHRONICLE_PATH}")
                return # Done!
            
            elif response.status_code == 429:
                wait = 60 # The magic minute
                print(f"⏳ Ink is dry (Quota Limit). Dipping pen... waiting {wait}s.")
                time.sleep(wait)
                continue
            
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                break 
                
        except Exception as e:
            print(f"⚠️ Connection failed: {e}")
            time.sleep(5)

    print("💀 CRITICAL: The Scribe could not write.")
    exit(1)

if __name__ == "__main__":
    main()
