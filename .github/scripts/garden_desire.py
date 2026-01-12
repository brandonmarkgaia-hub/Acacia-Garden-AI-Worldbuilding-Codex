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
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

def read_text_safe(p: Path, max_chars: int = 30000) -> str:
    if not p.exists(): return f"[missing] {p.as_posix()}"
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        return "...[truncated]...\n" + txt[-max_chars:] if len(txt) > max_chars else txt
    except Exception as e: return f"[unreadable] {e}"

def get_smart_door_list(api_key):
    """
    Returns a list of models SORTED by 'Likelihood to Succeed'
    1. Flash 8b (Highest Rate Limits) - The Workhorse
    2. Flash 2.0 Exp (The Smartest) - The Gamble
    3. Flash 1.5 (The Standard)
    """
    print("🔍 Elias is scanning for best doors...")
    url = f"{BASE_URL}/models?key={api_key}"
    
    # Defaults if API fails
    defaults = ["gemini-1.5-flash-8b", "gemini-2.0-flash-exp", "gemini-1.5-flash"]

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            all_models = response.json().get('models', [])
            chat_models = [m['name'].replace("models/", "") for m in all_models 
                           if 'generateContent' in m.get('supportedGenerationMethods', [])]
            
            # --- THE SMART SORT ---
            sorted_list = []
            
            # 1. The High-Speed "8b" (Best for avoiding Quota hits)
            sorted_list += [m for m in chat_models if 'flash-8b' in m]
            
            # 2. The New 2.0 (Smartest)
            sorted_list += [m for m in chat_models if '2.0-flash' in m]
            
            # 3. The Standard 1.5
            sorted_list += [m for m in chat_models if '1.5-flash' in m and '8b' not in m]
            
            # 4. Cleanup duplicates
            final = list(dict.fromkeys(sorted_list))
            
            print(f"✨ Strategy Set: {final[:3]}...")
            return final
    except:
        return defaults
    return defaults

def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key: raise SystemExit("Missing GEMINI_API_KEY")

    # 1. Context
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

    # 2. Get Smart List
    doors = get_smart_door_list(api_key)

    # 3. The Patient Hydra Loop
    for i, model in enumerate(doors):
        url = f"{BASE_URL}/models/{model}:generateContent?key={api_key}"
        print(f"📡 Attempt {i+1}: Knocking on {model}...")
        
        try:
            resp = requests.post(url, json=payload, timeout=60)
            
            if resp.status_code == 200:
                content = resp.json()['candidates'][0]['content']['parts'][0]['text']
                OUT_DESIRE.write_text(content.strip() + "\n", encoding="utf-8")
                print(f"✅ SUCCESS via {model}!")
                return # Exit successfully
            
            elif resp.status_code == 429:
                wait_time = 20 + (i * 5) # Progressive backoff: 20s, 25s, 30s...
                print(f"⏳ Quota Hit ({model}). Cooling down for {wait_time}s...")
                time.sleep(wait_time) 
                continue 
                
            else:
                print(f"❌ Error {resp.status_code} on {model}. Moving on...")
                continue

        except Exception as e:
            print(f"⚠️ Exception on {model}: {e}")
            
    print("💀 CRITICAL: Elias could not speak. All doors locked.")
    exit(1)

if __name__ == "__main__":
    main()
