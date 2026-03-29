#!/usr/bin/env python3
import os
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MUTATIONS_DIR = ROOT / "MUTATIONS"
MUTATIONS_DIR.mkdir(exist_ok=True)

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
        
        # --- 1. THE GREAT SWEEP (Cleanup Protocol) ---
        print("🧹 JANITOR: Clearing the nursery...")
        for pattern in ["MUTATION_Orchid_Issue_*", "MUTATION_EIDOLON_CODEX_*"]:
            for junk in MUTATIONS_DIR.glob(pattern):
                try:
                    os.remove(junk)
                    print(f"✅ Purged: {junk.name}")
                except Exception as e:
                    print(f"❌ Cleanup Error: {e}")

        # --- 2. ORCHID MANIFESTATION (GitHub CLI) ---
        for mutation in instructions.get("mutate", []):
            title = mutation['title']
            body = mutation['body']
            
            if "EIDOLON CODEX" in title or "Orchid Issue" in title:
                print(f"🌸 PLANTING REAL ORCHID: {title}")
                try:
                    subprocess.run([
                        "gh", "issue", "create", 
                        "--title", title, 
                        "--body", body,
                        "--label", "canonical-leaf"
                    ], check=True)
                except Exception as e:
                    print(f"❌ GH CLI Error: {e}")
            else:
                clean_title = "".join([c if c.isalnum() else "_" for c in title])
                (MUTATIONS_DIR / f"MUTATION_{clean_title}.md").write_text(body, encoding="utf-8")
                print(f"🧬 LORE: Created {clean_title}")

        # --- 3. DEEP JSON PATCHING ---
        for update in instructions.get("update", []):
            target_path = ROOT / update['file']
            if target_path.exists():
                data_file = json.loads(target_path.read_text())
                keys = update.get('key', 'navigation').split('.')
                curr = data_file
                for key in keys[:-1]:
                    curr = curr.setdefault(key, {})
                curr[keys[-1]] = update.get('data')
                target_path.write_text(json.dumps(data_file, indent=2), encoding="utf-8")
                print(f"🛠️ REPAIR: Patched {update['file']}")

    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__": main()
