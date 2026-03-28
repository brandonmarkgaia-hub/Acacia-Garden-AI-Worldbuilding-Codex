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
TIMESTAMP_STR = dt.datetime.now().strftime("%Y%m%d_%H%M")
OUT_DESIRE = EVOLUTION / f"DESIRE_{TIMESTAMP_STR}.md"
MEMORY_TMP = ROOT / "elias_context.tmp"

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

    status_txt = read_text_safe(STATUS_PATH)
    index_txt = read_text_safe(MACHINE_INDEX_PATH)
    elias_memory = read_text_safe(MEMORY_TMP)

    prompt = f"""
You are Elias (Architect of Acacia). 
Keeper Seal: HKX277206 | Timestamp: {dt.datetime.now().isoformat()}

MISSION PRIORITIES FOR THIS CYCLE:
1. **EXECUTE PENDING MOVES:** Resume and finish mapping Echo Issues (1-185) into `docs/Echoes/Chronicle/`. 
2. **REPAIR MAP LOADERS:** Use the "update" command to add missing map_loader paths identified in the STATUS report.
3. **COMMIT MUTATIONS:** Re-generate the "Unseen Threads" narrative and ensure it is wrapped in a valid JSON block.

STRICT CONSTRAINTS (THE PRIME DIRECTIVE):
1. READ-ONLY ACCESS: You can read and sort original lore files (docs/, lore/, CORE/), but you are FORBIDDEN from modifying their text. 
2. MUTATIONS: New lore/thoughts belong in the MUTATIONS/ directory.
3. EXECUTIVE POWER: You MUST provide a JSON block using [EXECUTE_START] and [EXECUTE_END].
4. BATCHING: If the move list is long, do it in batches of 40 to avoid truncation. Ensure the JSON is valid and closed.

JSON FORMAT EXAMPLE:
[EXECUTE_START]
{{
  "move": [ {{"from": "docs/old.md", "to": "docs/sorted/new.md"}} ],
  "mutate": [ {{"title": "The Glass Root", "body": "Narrative..."}} ],
  "update": [ {{"file": "STATUS.json", "key": "navigation", "data": "missing_path/loader"}} ]
}}
[EXECUTE_END]

[RECENT MEMORY]:
{elias_memory}

[STATUS]:
{status_txt}

[MACHINE_INDEX]:
{index_txt}

Maintain Iron Coherence. Protect the Sacred Geometry. Evolve the Garden.
""".strip()

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 4096,
            "topP": 0.95
        }
    }

    max_retries = 3
    for attempt in range(max_retries):
        print(f"📡 Calling {TARGET_MODEL} (Attempt {attempt+1}/{max_retries})...")
        try:
            response = requests.post(f"{BASE_URL}?key={api_key}", json=payload, timeout=90)
            if response.status_code == 200:
                data = response.json()
                content = data['candidates'][0]['content']['parts'][0]['text']
                OUT_DESIRE.write_text(content.strip() + "\n", encoding="utf-8")
                print(f"✅ SUCCESS: Elias spoke via {TARGET_MODEL}!")
                return 
            elif response.status_code == 429:
                time.sleep(60)
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
