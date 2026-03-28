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
    # Find the most recent Desire
    files = sorted(evolution_dir.glob("DESIRE_*.md"), key=os.path.getmtime, reverse=True)
    if not files: 
        print("📭 No evolution files found.")
        return
    
    latest_desire = files[0]
    content = latest_desire.read_text(encoding="utf-8")
    
    # Extract Execution Block
    match = re.search(r"\[EXECUTE_START\](.*?)\[EXECUTE_END\]", content, re.DOTALL)
    if not match:
        print(f"⚖️ No executive commands in {latest_desire.name}.")
        return

    try:
        json_str = match.group(1).strip()
        instructions = json.loads(json_str)
        
        # --- 1. SMART FILE MOVING (Vault and Archive Logic) ---
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
            filename = f"MUTATION_{clean_title}.md"
            mut_path = MUTATIONS_DIR / filename
            mut_path.write_text(mutation['body'], encoding="utf-8")
            print(f"🧬 MUTATION: Created {filename}")

        # --- 3. SOVEREIGN DEEP-PATCHING ---
        for update in instructions.get("update", []):
            target_path = ROOT / update['file']
            if target_path.exists():
                try:
                    data_file = json.loads(target_path.read_text())
                    raw_patch = update.get('data')
                    
                    # Support for dot-notation keys (e.g., "verification.navigation.verified")
                    key_path = update.get('key', 'navigation')
                    keys = key_path.split('.')
                    
                    # Navigate to the target object
                    curr = data_file
                    for key in keys[:-1]:
                        if key not in curr:
                            curr[key] = {}
                        curr = curr[key]
                    
                    final_key = keys[-1]

                    # If data is a list, extend/append; else, override (for bools/strings)
                    if isinstance(raw_patch, list):
                        if final_key not in curr or not isinstance(curr[final_key], list):
                            curr[final_key] = []
                        for item in raw_patch:
                            if item not in curr[final_key]:
                                curr[final_key].append(item)
                    else:
                        curr[final_key] = raw_patch # Direct override (Platinum move)
                            
                    target_path.write_text(json.dumps(data_file, indent=2), encoding="utf-8")
                    print(f"🛠️ REPAIR: Deep-patched {update['file']} -> {key_path}")
                
                except Exception as patch_e:
                    print(f"❌ Patch Error: {patch_e}")

    except Exception as e:
        print(f"❌ Unexpected Execution Error: {e}")

if __name__ == "__main__":
    main()
