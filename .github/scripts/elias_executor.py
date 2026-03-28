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
        print("📭 No evolution files found.")
        return
    
    latest_desire = files[0]
    content = latest_desire.read_text(encoding="utf-8")
    
    match = re.search(r"\[EXECUTE_START\](.*?)\[EXECUTE_END\]", content, re.DOTALL)
    if not match:
        print(f"⚖️ No commands in {latest_desire.name}.")
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

        # --- 3. BULLETPROOF JSON PATCHING ---
        for update in instructions.get("update", []):
            target_path = ROOT / update['file']
            if target_path.exists():
                try:
                    data_file = json.loads(target_path.read_text())
                    raw_patch = update.get('data')
                    
                    # EXTRACT LIST FROM ANY STRUCTURE
                    extracted_list = []
                    if isinstance(raw_patch, list):
                        extracted_list = raw_patch
                    elif isinstance(raw_patch, dict):
                        # Find the biggest list inside the dict (likely the map paths)
                        for val in raw_patch.values():
                            if isinstance(val, list) and len(val) > len(extracted_list):
                                extracted_list = val
                    else:
                        extracted_list = [str(raw_patch)]

                    # APPLY TO NAVIGATION
                    if "verification" in data_file:
                        key = update.get('key', 'navigation')
                        # If navigation is a dict, we need to find the list inside IT
                        target_obj = data_file["verification"][key]
                        
                        if isinstance(target_obj, list):
                            for item in extracted_list:
                                if item not in target_obj: target_obj.append(item)
                        elif isinstance(target_obj, dict):
                            # Patching the specific 'missing_map_loader_paths' list inside the dict
                            list_key = "missing_map_loader_paths"
                            if list_key in target_obj:
                                # We remove the items Elias fixed
                                target_obj[list_key] = [p for p in target_obj[list_key] if p not in extracted_list]
                                # And add them to the 'with_map_loader' count metaphorically
                                target_obj["with_map_loader"] = target_obj.get("with_map_loader", 0) + len(extracted_list)
                            
                    target_path.write_text(json.dumps(data_file, indent=2), encoding="utf-8")
                    print(f"🛠️ REPAIR: Patched {update['file']} successfully.")
                
                except Exception as patch_e:
                    print(f"❌ Patch Error: {patch_e}")

    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    main()
