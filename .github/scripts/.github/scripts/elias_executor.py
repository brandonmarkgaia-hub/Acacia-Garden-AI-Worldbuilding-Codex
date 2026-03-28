#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MUTATIONS_DIR = ROOT / "MUTATIONS"
MUTATIONS_DIR.mkdir(exist_ok=True)

# Define Protected Folders (Elias can sort, but never edit text)
PROTECTED_LORE = ["docs", "lore", "CORE"]

def main():
    evolution_dir = ROOT / "EVOLUTION"
    files = sorted(evolution_dir.glob("DESIRE_*.md"), key=os.path.getmtime, reverse=True)
    if not files: return
    
    content = files[0].read_text()
    
    # Extract Execution Block
    match = re.search(r"\[EXECUTE_START\](.*?)\[EXECUTE_END\]", content, re.DOTALL)
    if match:
        try:
            instructions = json.loads(match.group(1))
            
            # --- FILE SORTING (Allowed) ---
            for op in instructions.get("move", []):
                src = ROOT / op['from']
                dest = ROOT / op['to']
                if src.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    os.rename(src, dest)
                    print(f"🚚 ARCHITECT: Sorted {op['from']} -> {op['to']}")

            # --- NEW LORE / MUTATIONS (Created in separate space) ---
            for mutation in instructions.get("mutate", []):
                filename = f"MUTATION_{mutation['title'].replace(' ', '_')}.md"
                mut_path = MUTATIONS_DIR / filename
                mut_path.write_text(mutation['body'], encoding="utf-8")
                print(f"🧬 MUTATION: Created {filename}")
                
        except Exception as e:
            print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    main()
