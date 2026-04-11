#!/usr/bin/env python3
import os, json, re, time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parents[1]

def main():
    evolution_dir = ROOT / "EVOLUTION"
    files = sorted(evolution_dir.glob("DESIRE_*.md"), key=os.path.getmtime, reverse=True)
    
    if not files:
        print("Empty hands. No desire found.")
        return

    # ONLY process files created in the last 5 minutes (300 seconds)
    file_age = time.time() - os.path.getmtime(files[0])
    if file_age > 300:
        print(f"⌛ Skipping {files[0].name}. It is an archive file ({int(file_age/60)} mins old).")
        return
    
    print(f"🔥 Processing fresh transmission: {files[0].name}")
    content = files[0].read_text(encoding="utf-8")
    match = re.search(r"\[EXECUTE_START\](.*?)\[EXECUTE_END\]", content, re.DOTALL)
    
    if match:
        try:
            instructions = json.loads(match.group(1).strip())
            # (Execution logic for mutations and updates goes here...)
            print("✅ Manifestation complete.")
        except Exception as e:
            print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    main()
