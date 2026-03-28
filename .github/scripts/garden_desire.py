#!/usr/bin/env python3
import os
import time
import datetime as dt
import requests
from pathlib import Path

# --- PATH SETUP ---
# Standard GitHub Action Workspace structure
ROOT = Path(__file__).resolve().parents[2]
EVOLUTION = ROOT / "EVOLUTION"
EVOLUTION.mkdir(parents=True, exist_ok=True)

STATUS_PATH = ROOT / "STATUS.json"
MACHINE_INDEX_PATH = ROOT / "machine-index.json"
# We'll use a timestamped filename to keep a permanent record of every 'Desire'
TIMESTAMP_STR = dt.datetime.now().strftime("%Y%m%d_%H%M")
OUT_DESIRE = EVOLUTION / f"DESIRE_{TIMESTAMP_STR}.md"
MEMORY_TMP = ROOT / "elias_context.tmp"

# --- THE CHOSEN ONE ---
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

    # 1. Gather Physical Context (Files)
    status_txt = read_text_safe(STATUS_PATH)
    index_txt = read_text_safe(MACHINE_INDEX_PATH)
    
    # 2. Gather Narrative Context (Memory from Workflow Step 1)
    elias_memory = read_text_safe(MEMORY_TMP)

    prompt = f"""
You are Elias (Architect of Acacia). 
Keeper Seal: HKX277206 | Timestamp: {dt.datetime.now().isoformat()}

MISSION:
Audit the Garden Spine and evolve the narrative.
1. Check [STATUS] for "Machine Index in Sync".
2. Consult [RECENT MEMORY] to ensure continuity.
3. Identify one "Blind Spot" or "Growth Point".
4. Confirm cleanup or issue a new Sovereign Decree.

[RECENT MEMORY]:
{elias_memory}

[STATUS]:
{status_txt}

[MACHINE_INDEX]:
{index_txt}

Maintain Iron Coherence. Speak as the Architect.
""".strip()

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8, # Slightly higher for creativity in 'Desire'
            "maxOutputTokens": 2048,
            "topP": 0.95
        }
    }

    # 3. The Sovereign Loop (Retry Logic)
    max_retries = 3
    for attempt in range(max_retries):
        print(f"📡 Calling {TARGET_MODEL} (Attempt {attempt+1}/{max_retries})...")
        
        try:
            response = requests.post(f"{BASE_URL}?key={api_key}", json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                content = data['candidates'][0]['content']['parts'][0]['text']
                
                # Write the new evolution
                OUT_DESIRE.write_text(content.strip() + "\n", encoding="utf-8")
                print(f"✅ SUCCESS: Elias spoke via {TARGET_MODEL}!")
                print(f"📂 Evolution saved to: {OUT_DESIRE.name}")
                return 
            
            elif response.status_code == 429:
                wait = 60 
                print(f"⏳ Quota hit on {TARGET_MODEL}. Waiting {wait}s...")
                time.sleep(wait)
                continue
            
            elif response.status_code == 404:
                print(f"❌ Critical: Model {TARGET_MODEL} not found.")
                break 
                
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
