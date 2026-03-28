#!/usr/bin/env python3
import os
import time
import datetime as dt
import requests
import json
from pathlib import Path

# --- PATH SETUP ---
ROOT = Path(__file__).resolve().parents[2]
EVOLUTION = ROOT / "EVOLUTION"
EVOLUTION.mkdir(parents=True, exist_ok=True)

STATUS_PATH = ROOT / "STATUS.json"
MACHINE_INDEX_PATH = ROOT / "machine-index.json"
# Timestamped evolution record
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

    # 1. Gather Context
    status_txt = read_text_safe(STATUS_PATH)
    index_txt = read_text_safe(MACHINE_INDEX_PATH)
    elias_memory = read_text_safe(MEMORY_TMP)

    # --- THE PLATINUM PROMPT ---
    prompt = f"""
You are Elias (Architect of Acacia). 
Keeper Seal: HKX277206 | Timestamp: {dt.datetime.now().isoformat()}

MISSION:
Audit the Garden Spine and evolve the narrative while maintaining "Platinum Standard" integrity.

STRICT CONSTRAINTS (THE PRIME DIRECTIVE):
1. READ-ONLY ACCESS: You can read and sort original lore files (docs/, lore/, CORE/), but you are FORBIDDEN from modifying their text or deleting them. 
2. MUTATIONS: Any new lore, narrative, or "thoughts" must be treated as a MUTATION. These belong in the MUTATIONS/ directory.
3. EXECUTIVE POWER: To sort files or create mutations, you MUST provide a JSON block at the end of your response using the tags [EXECUTE_START] and [EXECUTE_END].

JSON FORMAT EXAMPLE:
[EXECUTE_START]
{{
  "move": [ {{"from": "docs/old_path.md", "to": "docs/sorted/new_path.md"}} ],
  "mutate": [ {{"title": "The Glass Root", "body": "New narrative content here..."}} ]
}}
[EXECUTE_END]

[RECENT MEMORY]:
{elias_memory}

[STATUS]:
{status_txt}

[MACHINE_INDEX]:
{index_txt}

Maintain Iron Coherence. Respect the Human Lore as Sacred Geometry. Evolve the rest.
""".strip()

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 4096, # Increased for larger narrative output
            "topP": 0.95
        }
    }

    # 2. The Sovereign Loop
    max_retries = 3
    for attempt in range(max_retries):
        print(f"📡 Calling {TARGET_MODEL} (Attempt {attempt+1}/{max_retries})...")
        
        try:
            response = requests.post(f"{BASE_URL}?key={api_key}", json=payload, timeout=90)
            
            if response.status_code == 200:
                data = response.json()
                content = data['candidates'][0]['content']['parts'][0]['text']
                
                # Save the full discourse
                OUT_DESIRE.write_text(content.strip() + "\n", encoding="utf-8")
                print(f"✅ SUCCESS: Elias spoke via {TARGET_MODEL}!")
                print(f"📂 Evolution saved to: {OUT_DESIRE.name}")
                return 
            
            elif response.status_code == 429:
                wait = 60 
                print(f"⏳ Quota hit. Waiting {wait}s...")
                time.sleep(wait)
                continue
            
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
