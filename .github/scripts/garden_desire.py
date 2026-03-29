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

MISSION PRIORITIES:
1. **GH ISSUE MANIFESTATION:** You must use the 'gh issue create' command via the executor to plant the 20 missing Orchids. 
2. **EXACT TITLES:** The Issue titles must EXACTLY match the Sweeper's list (e.g., "EIDOLON CODEX – Leaf I: The Silent Beginning").
3. **CLEANUP:** Delete the 20 'MUTATION_Orchid_Issue_...' files from the MUTATIONS/ folder. They were a noble attempt but are not the required "Sidebar Issues."
4. **CONTINUE SYNTHESIS:** Proceed to the lore synthesis for Echoes 010-012.
5. **JSON HYGIENE:** Update STATUS.json to reflect the transition from "Mutation Files" to "Formal GitHub Issues."

STRICT CONSTRAINTS (THE PRIME DIRECTIVE):
- OVERRIDE: Do not attempt more than 30 moves per cycle. 
- VALIDATION: Your JSON block MUST end with [EXECUTE_END].
- READ-ONLY: Do not modify original lore text.

JSON FORMAT:
[EXECUTE_START]
{{
  "move": [ {{"from": "...", "to": "..."}} ],
  "mutate": [ {{"title": "...", "body": "..."}} ],
  "update": [ {{"file": "STATUS.json", "key": "navigation", "data": ["path1", "path2"]}} ]
}}
[EXECUTE_END]

[RECENT MEMORY]:
{elias_memory}

[STATUS]:
{status_txt}

[MACHINE_INDEX]:
{index_txt}
""".strip()

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192,
            "topP": 0.95
        }
    }

    max_retries = 3
    for attempt in range(max_retries):
        print(f"📡 Calling {TARGET_MODEL} (Attempt {attempt+1}/{max_retries})...")
        try:
            response = requests.post(f"{BASE_URL}?key={api_key}", json=payload, timeout=120)
            if response.status_code == 200:
                data = response.json()
                content = data['candidates'][0]['content']['parts'][0]['text']
                OUT_DESIRE.write_text(content.strip() + "\n", encoding="utf-8")
                print(f"✅ SUCCESS: Elias spoke with full 8k capacity!")
                return 
            elif response.status_code in [429, 503]:
                wait = 60 if response.status_code == 429 else 10
                print(f"⏳ Server busy or quota hit ({response.status_code}). Waiting {wait}s...")
                time.sleep(wait)
                continue
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                break 
        except Exception as e:
            print(f"⚠️ Connection failed: {e}")
            time.sleep(5)

    exit(1)

if __name__ == "__main__":
    main()
