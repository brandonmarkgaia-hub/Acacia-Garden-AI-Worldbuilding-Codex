#!/usr/bin/env python3
import os, json, re
from pathlib import Path

# --- PATH SETUP ---
SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parents[1]

def main():
    evolution_dir = ROOT / "EVOLUTION"
    mutations_dir = ROOT / "MUTATIONS"
    mutations_dir.mkdir(exist_ok=True)

    # Find the newest Desire file
    files = sorted(evolution_dir.glob("DESIRE_*.md"), key=os.path.getmtime, reverse=True)
    if not files: 
        print("Empty hands. No desire found.")
        return
    
    content = files[0].read_text(encoding="utf-8")
    match = re.search(r"\[EXECUTE_START\](.*?)\[EXECUTE_END\]", content, re.DOTALL)
    if not match: 
        print("No execution instructions found.")
        return

    try:
        instructions = json.loads(match.group(1).strip())
        
        # 1. Mutate Files
        for mutation in instructions.get("mutate", []):
            if mutation['title'] == "COMMUNICATIONS.md":
                target_path = ROOT / "COMMUNICATIONS.md"
            else:
                clean_title = "".join([c if c.isalnum() else "_" for c in mutation['title']])
                target_path = mutations_dir / f"{clean_title}.md"
                
            target_path.write_text(mutation['body'], encoding="utf-8")
            print(f"📝 Manifested: {target_path.name}")

        # 2. Update JSON
        for update in instructions.get("update", []):
            target = ROOT / update['file']
            if target.exists():
                data = json.loads(target.read_text())
                data[update['key']] = update['data']
                target.write_text(json.dumps(data, indent=2))
                print(f"⚙️ Updated {target.name}: {update['key']}")

    except Exception as e: 
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__": 
    main()
