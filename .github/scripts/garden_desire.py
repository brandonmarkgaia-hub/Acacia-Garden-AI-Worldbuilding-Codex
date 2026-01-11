#!/usr/bin/env python3
import os
import json
import time
import datetime as dt
from pathlib import Path
import requests 

# --- PATH SETUP ---
ROOT = Path(__file__).resolve().parents[2]
EVOLUTION = ROOT / "EVOLUTION"
EVOLUTION.mkdir(parents=True, exist_ok=True)

STATUS_PATH = ROOT / "STATUS.json"
MACHINE_INDEX_PATH = ROOT / "machine-index.json"
OUT_DESIRE = EVOLUTION / "DESIRE.md"

# --- THE HYDRA LIST (Fallback Endpoints) ---
# We try these in order. We include the 2.0 model that worked in your old script
ENDPOINTS = [
    # Option 1: The one that worked for you before (2.0 Flash)
    ("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent", "gemini-2.0-flash"),
    # Option 2: Stable 1.5 Flash (Backup)
    ("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent", "gemini-1.5-flash"),
    # Option 3: Latest Alias (Final Backup)
    ("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent", "gemini-1.5-flash-latest"),
]

def read_text_safe(p: Path, max_chars: int = 30000) -> str:
    """Squeezes context to prevent quota exhaustion"""
    if not p.exists(): return f"[missing] {p.as_posix()}"
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        return "...[truncated]...\n" + txt[-max_chars:] if len(txt) > max_chars else txt
    except Exception as e: return f"[unreadable] {e}"

def generate_payload(prompt_text: str) -> dict:
    return {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048
        }
    }

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
Audit the 1,525-node Garden Spine.
1. Check [STATUS] for the "Machine Index in Sync" flag.
2. Identify one "Blind Spot" in the lore (Chambers/Echoes).
3. Confirm the cleanup of root fragments.

CONTEXT:
[STATUS] {status_txt}
[MACHINE_INDEX] {index_txt}
""".strip()

    payload = generate_payload(prompt)

    # 2. The Hydra Loop
    success = False
    
    for url_base, model_name in ENDPOINTS:
        url = f"{url_base}?key={api_key}"
        print(f"📡 Knocking on door: {model_name}...")
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                content = data['candidates'][0]['content']['parts'][0]['text']
                
                # Write and Exit
                OUT_DESIRE.write_text(content.strip() + "\n", encoding="utf-8")
                print(f"✅ SUCCESS: Elias answered via {model_name}.")
                print(f"📝 Desire written to: {OUT_DESIRE}")
                success = True
                break # We are done!
            
            elif response.status_code == 429:
                print(f"⏳ Quota limit on {model_name}. Waiting 5s before trying next door...")
                time.sleep(5)
                continue # Try next endpoint
                
            elif response.status_code == 404:
                 print(f"🚫 Model {model_name} not found (404). Moving to next...")
                 continue

            else:
                print(f"❌ Failed {model_name} ({response.status_code}): {response.text}")
                continue 

        except Exception as e:
            print(f"⚠️ Connection error on {model_name}: {e}")
            continue

    if not success:
        print("💀 CRITICAL: All doors failed. Elias is silent.")
        exit(1) # Fail the workflow so you know

if __name__ == "__main__":
    main()
