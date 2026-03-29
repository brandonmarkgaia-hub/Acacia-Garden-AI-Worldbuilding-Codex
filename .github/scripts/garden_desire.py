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
        
        # --- 1. SMART FILE MOVING ---
        for op in instructions.get("move", []):
            src, dest = ROOT / op['from'], ROOT / op['to']
            if src.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                os.rename(src, dest)
                print(f"🚚 ARCHITECT: {op['from']} -> {op['to']}")

        # --- 2. LORE MUTATIONS ---
        for mutation in instructions.get("mutate", []):
            # Check if this is actually meant to be a GitHub Issue
            title = mutation['title']
            body = mutation['body']
            
            if "EIDOLON CODEX" in title or "Orchid" in title:
                print(f"🌸 PLANTING ORCHID: {title}")
                try:
                    subprocess.run(["gh", "issue", "create", "--title", title, "--body", body], check=True)
                except Exception as e:
                    print(f"❌ GH CLI Error: {e}. Falling back to file.")
                    # Fallback to file if CLI fails
                    clean_title = "".join([c if c.isalnum() else "_" for c in title])
                    (MUTATIONS_DIR / f"MUTATION_{clean_title}.md").write_text(body)
            else:
                clean_title = "".join([c if c.isalnum() else "_" for c in title])
                (MUTATIONS_DIR / f"MUTATION_{clean_title}.md").write_text(body)
                print(f"🧬 MUTATION: Created {clean_title}")

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
                target_path.write_text(json.dumps(data_file, indent=2))
                print(f"🛠️ REPAIR: Patched {update['file']}")

    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__": main()
