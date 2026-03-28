#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path

# --- PATH SETUP ---
ROOT = Path(__file__).resolve().parents[2]
MUTATIONS_DIR = ROOT / "MUTATIONS"
MUTATIONS_DIR.mkdir(exist_ok=True)

# Define Protected Folders (Read/Move only, never overwrite)
PROTECTED_LORE = ["docs", "lore", "CORE"]

def main():
    evolution_dir = ROOT / "EVOLUTION"
    # Find the most recent Desire
    files = sorted(evolution_dir.glob("DESIRE_*.md"), key=os.path.getmtime, reverse=True)
    if not files: 
        print("📭 No evolution files found to execute.")
        return
    
    latest_desire = files[0]
    content = latest_desire.read_text(encoding="utf-8")
    
    # Extract Execution Block using Regex
    match = re.search(r"\[EXECUTE_START\](.*?)\[EXECUTE_END\]", content, re.DOTALL)
    if not match:
        print(f"⚖️ Elias spoke in {latest_desire.name}, but issued no executive commands.")
        return

    try:
        # Clean the extracted text to ensure it's valid JSON
        json_str = match.group(1).strip()
        instructions = json.loads(json_str)
        
        # --- 1. FILE SORTING (Moving files to better paths) ---
        for op in instructions.get("move", []):
            src = ROOT / op['from']
            dest = ROOT / op['to']
            if src.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                # Ensure we don't move into a non-existent or restricted volume
                os.rename(src, dest)
                print(f"🚚 ARCHITECT: Sorted {op['from']} -> {op['to']}")
            else:
                print(f"⚠️ Missing Source: {op['from']}")

        # --- 2. NEW LORE / MUTATIONS (Emergent narratives) ---
        for mutation in instructions.get("mutate", []):
            # Sanitize title for filename
            clean_title = "".join([c if c.isalnum() else "_" for c in mutation['title']])
            filename = f"MUTATION_{clean_title}.md"
            mut_path = MUTATIONS_DIR / filename
            mut_path.write_text(mutation['body'], encoding="utf-8")
            print(f"🧬 MUTATION: Created {filename}")

        # --- 3. JSON PATCHING (Repairing Status/Map Loaders) ---
        for update in instructions.get("update", []):
            target_path = ROOT / update['file']
            if target_path.exists():
                try:
                    data = json.loads(target_path.read_text())
                    
                    # Logic specifically for map_loader/verification patching
                    if "verification" in data:
                        # Append new data if it's a list, or update the key
                        key = update.get('key', 'navigation')
                        if key in data['verification']:
                            data['verification'][key].append(update['data'])
                            target_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
                            print(f"🛠️ REPAIR: Patched {update['file']} entry: {update['data']}")
                except Exception as patch_e:
                    print(f"❌ Patch Error on {update['file']}: {patch_e}")

    except json.JSONDecodeError:
        print(f"⚠️ JSON ERROR: Elias's decree in {latest_desire.name} was truncated or malformed.")
    except Exception as e:
        print(f"❌ Unexpected Execution Error: {e}")

if __name__ == "__main__":
    main()
