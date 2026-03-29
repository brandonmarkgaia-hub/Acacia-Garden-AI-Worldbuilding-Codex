#!/usr/bin/env python3
import os, json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MUTATIONS_DIR = ROOT / "MUTATIONS"

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
            title, body = mutation['title'], mutation['body']
            
            # If it's a sidebar item, check if it exists first
            if any(word in title.upper() for word in ["EIDOLON", "CODEX", "ORCHID"]):
                check = subprocess.run(["gh", "issue", "list", "--search", title, "--json", "number"], capture_output=True, text=True)
                if not json.loads(check.stdout):
                    print(f"🌸 PLANTING: {title}")
                    subprocess.run(["gh", "issue", "create", "--title", title, "--body", body], check=True)
                else:
                    print(f"🌿 ALREADY BLOOMING: {title}")
            else:
                clean_title = "".join([c if c.isalnum() else "_" for c in title])
                (MUTATIONS_DIR / f"MUTATION_{clean_title}.md").write_text(body, encoding="utf-8")
                print(f"🧬 LORE: Created {clean_title}")

        for update in instructions.get("update", []):
            target = ROOT / update['file']
            if target.exists():
                data = json.loads(target.read_text())
                data[update.get('key', 'status')] = update.get('data')
                target.write_text(json.dumps(data, indent=2))
                print(f"🛠️ REPAIR: Patched {update['file']}")

    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__": main()
