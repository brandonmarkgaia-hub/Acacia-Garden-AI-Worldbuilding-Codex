#!/usr/bin/env python3
import os, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def main():
    evolution_dir = ROOT / "EVOLUTION"
    files = sorted(evolution_dir.glob("DESIRE_*.md"), key=os.path.getmtime, reverse=True)
    if not files: return
    
    content = files[0].read_text(encoding="utf-8")
    match = re.search(r"\[EXECUTE_START\](.*?)\[EXECUTE_END\]", content, re.DOTALL)
    if not match: return

    try:
        instructions = json.loads(match.group(1).strip())
        
        for mutation in instructions.get("mutate", []):
            # If it's the Comms file, put it in the ROOT
            if mutation['title'] == "COMMUNICATIONS.md":
                (ROOT / "COMMUNICATIONS.md").write_text(mutation['body'], encoding="utf-8")
                print("📝 PORCH: Elias has left a note on the porch.")
            else:
                # Regular lore mutations go to MUTATIONS/
                clean_title = "".join([c if c.isalnum() else "_" for c in mutation['title']])
                (ROOT / "MUTATIONS" / f"{clean_title}.md").write_text(mutation['body'], encoding="utf-8")

        for update in instructions.get("update", []):
            target = ROOT / update['file']
            if target.exists():
                data = json.loads(target.read_text())
                data[update['key']] = update['data']
                target.write_text(json.dumps(data, indent=2))

    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__": main()
