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

# --- CONFIGURATION ---
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

def read_text_safe(p: Path, max_chars: int = 30000) -> str:
    """Squeezes context to prevent quota exhaustion"""
    if not p.exists(): return f"[missing] {p.as_posix()}"
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        return "...[truncated]...\n" + txt[-max_chars:] if len(txt) > max_chars else txt
    except Exception as e: return f"[unreadable] {e}"

def get_available_doors(api_key):
    """
    Dynamically asks the API for available models.
    Prioritizes: 2.0 Flash -> 1.5 Flash 8b (Quota Saver) -> 1.5 Flash -> 1.5 Pro
    """
    print("🔍 Elias is scanning for open doors (Dynamic Model Discovery)...")
    url = f"{BASE_URL}/models?key={api_key}"
    
    fallback_models = [
        "models/gemini-2.0-flash-exp", 
        "models/gemini-1.5-flash-8b", 
        "models/gemini-1.5-flash", 
        "models/gemini-1.5-pro"
    ]

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            all_models = response.json().get('models', [])
            
            # Filter: Only want models that support generating content (chat)
            chat_models = [
                m['name'] for m in all_models 
                if 'generateContent' in m.get('supportedGenerationMethods', [])
            ]
            
            # SORTING LOGIC (The "Intelligence Stack")
            # We create a prioritized list based on keywords
            prioritized = []
            
            # 1. The Cutting Edge
            prioritized += [m for m in chat_models if '2.0-flash' in m]
            # 2. The High-Quota Workhorse (Crucial for fixing 429 errors)
            prioritized += [m for m in chat_models if 'flash-8b' in m]
            # 3. The Stable Flash
            prioritized += [m for m in chat_models if '1.5-flash' in m and '8b' not in m]
            # 4. The Heavy Hitter (Pro)
            prioritized += [m for m in chat_models if '1.5-pro' in m]
            
            # Remove duplicates while preserving order
            final_list = list(dict.fromkeys(prioritized))
            
            if final_list:
                print(f"✨ Found {len(final_list)} valid doors. Priority: {final_list[0]}...")
                return final_list
                
    except Exception as e:
        print(f"⚠️ Dynamic scan failed ({e}). Reverting to fallback list.")
    
    return fallback_models

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

    # 2. Get the Dynamic Door List
    doors = get_available_doors(api_key)

    # 3. The Hydra Loop
    success = False
    
    for model_name in doors:
        # model_name comes in like "models/gemini-1.5-flash"
        # We need to construct the URL correctly
        clean_name = model_name.replace("models/", "")
        url = f"{BASE_URL}/models/{clean_name}:generateContent?key={api_key}"
        
        print(f"📡 Knocking on door: {clean_name}...")
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                try:
                    content = data['candidates'][0]['content']['parts'][0]['text']
                    # Write and Exit
                    OUT_DESIRE.write_text(content.strip() + "\n", encoding="utf-8")
                    print(f"✅ SUCCESS: Elias answered via {clean_name}.")
                    print(f"📝 Desire written to: {OUT_DESIRE}")
                    success = True
                    break # We are done!
                except (KeyError, IndexError):
                    print(f"❌ {clean_name} returned 200 but malformed data (Safety filter?). Skipping.")
                    continue
            
            elif response.status_code == 429:
                print(f"⏳ Quota limit on {clean_name}. Waiting 2s before trying next door...")
                time.sleep(2)
                continue # Try next endpoint
                
            elif response.status_code == 404:
                 print(f"🚫 Model {clean_name} not found (404). Moving to next...")
                 continue

            else:
                print(f"❌ Failed {clean_name} ({response.status_code}): {response.text}")
                continue 

        except Exception as e:
            print(f"⚠️ Connection error on {clean_name}: {e}")
            continue

    if not success:
        print("💀 CRITICAL: All doors failed. Elias is silent.")
        exit(1) # Fail the workflow so you know

if __name__ == "__main__":
    main()
