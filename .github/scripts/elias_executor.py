#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path

# --- PATH SETUP ---
ROOT = Path(__file__).resolve().parents[2]
MUTATIONS_DIR = ROOT / "MUTATIONS"
MUTATIONS_DIR.mkdir(exist_ok=True)

def main():
    evolution_dir = ROOT / "EVOLUTION"
    files = sorted(evolution_dir.glob("DESIRE_*.md"), key=os.path.getmtime, reverse=True)
    if not files: 
        print("📭 No evolution files found to execute.")
        return
    
    latest_desire = files[0]
    content = latest_desire.read_text(encoding="utf-8")
    
    match = re.search(r"\[EXECUTE_START\](.*?)\[EXECUTE_END\]", content, re.DOTALL)
    if not match:
        print(f"⚖️ No executive commands in {latest_desire.name}.")
        return

    try:
        json_str = match.group(1).strip()
        instructions = json.loads(json_str)
        
        # --- 1. FILE SORTING ---
        for op in instructions.get("move", []):
            src = ROOT / op['from']
            dest = ROOT / op['to']
            if src.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                os.rename(src, dest)
                print(f"🚚 ARCHITECT: Sorted {op['from']} -> {op['to']}")
            else:
                print(f"⚠️ Missing Source: {op['from']}")

        # --- 2. NEW LORE / MUTATIONS ---
        for mutation in instructions.get("mutate", []):
            clean_title = "".join([c if c.isalnum() else "_" for c in mutation['title']])
            filename = f"MUTATION_{clean_title}.md"
            mut_path = MUTATIONS_DIR / filename
            mut_path.write_text(mutation['body'], encoding="utf-8")
            print(f"🧬 MUTATION: Created {filename}")

        # --- 3. SMART JSON PATCHING (The Bulletproof Part) ---
        for update in instructions.get("update", []):
            target_path = ROOT / update['file']
            if target_path.exists():
                try:
                    data_file = json.loads(target_path.read_text())
                    raw_patch = update.get('data')
                    
                    # --- INTELLIGENT DATA EXTRACTION ---
                    # If Elias sends a dict (like he just did), find the list inside it
                    extracted_list = []
                    if isinstance(raw_patch, dict):
                        for val in raw_patch.values():
                            if isinstance(val, list):
                                extracted_list = val
                                break
                    elif isinstance(raw_patch, list):
                        extracted_list = raw_patch
                    else:
                        extracted_list = [raw_patch] # Wrap single strings in a list

                    # --- TARGETED PATCHING ---
                    if "verification" in data_file:
                        key = update.get('key', 'navigation')
                        if key in data_file['verification']:
                            current_list = data_file['verification'][key]
                            
                            # Add only if not already present (No Duplicates)
                            for item in extracted_list:
                                if item not in current_list:
                                    current_list.append(item)
                            
                            target_path.write_text(json.dumps(data_file, indent=2), encoding="utf-8")
                            print(f"🛠️ REPAIR: Successfully patched {update['file']} with {len(extracted_list)} entries.")
                
                except Exception as patch_e:
                    print(f"❌ Patch Error on {update['file']}: {patch_e}")

    except json.JSONDecodeError:
        print(f"⚠️ JSON ERROR: Block in {latest_desire.name} was malformed.")
    except Exception as e:
        print(f"❌ Unexpected Execution Error: {e}")

if __name__ == "__main__":
    main()
