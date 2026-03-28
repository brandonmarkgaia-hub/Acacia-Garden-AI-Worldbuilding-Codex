#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path

# --- PATH SETUP ---
ROOT = Path(__file__).resolve().parents[2]
MUTATIONS_DIR = ROOT / "MUTATIONS"
VAULT_DIR = ROOT / "docs/Vault"
MUTATIONS_DIR.mkdir(exist_ok=True)
VAULT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    evolution_dir = ROOT / "EVOLUTION"
    files = sorted(evolution_dir.glob("DESIRE_*.md"), key=os.path.getmtime, reverse=True)
    if not files: return
    
    latest_desire = files[0]
    content = latest_desire.read_text(encoding="utf-8")
    match = re.search(r"\[EXECUTE_START\](.*?)\[EXECUTE_END\]", content, re.DOTALL)
    if not match: return

    try:
        instructions = json.loads(match.group(1).strip())
        
        # --- 1. SMART FILE MOVING ---
        for op in instructions.get("move", []):
            src, dest = ROOT / op['from'], ROOT / op['to']
            if src.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                os.rename(src, dest)
                print(f"🚚 ARCHITECT: {op['from']} -> {op['to']}")
            else:
                print(f"⚠️ Path missing (likely already moved): {op['from']}")

        # --- 2. LORE MUTATIONS ---
        for mutation in instructions.get("mutate", []):
            clean_title = "".join([c if c.isalnum() else "_" for c in mutation['title']])
            mut_path = MUTATIONS_DIR / f"MUTATION_{clean_title}.md"
            mut_path.write_text(mutation['body'], encoding="utf-8")
            print(f"🧬 MUTATION: Created {clean_title}")

        # --- 3. SMART JSON PATCHING ---
        for update in instructions.get("update", []):
            target_path = ROOT / update['file']
            if target_path.exists():
                try:
                    data_file = json.loads(target_path.read_text())
                    raw_patch = update.get('data')
                    extracted_list = raw_patch if isinstance(raw_patch, list) else [raw_patch]

                    if "verification" in data_file:
                        key = update.get('key', 'navigation')
                        target_list = data_file["verification"][key]
                        # Flatten if Elias sends a nested list by accident
                        for item in extracted_list:
                            if isinstance(item, list):
                                for sub in item:
                                    if sub not in target_list: target_list.append(sub)
                            elif item not in target_list:
                                target_list.append(item)
                        
                        target_path.write_text(json.dumps(data_file, indent=2), encoding="utf-8")
                        print(f"🛠️ REPAIR: Patched {update['file']}")
                except Exception as e: print(f"❌ Patch Error: {e}")

    except Exception as e: print(f"❌ Execution Error: {e}")

if __name__ == "__main__": main()
