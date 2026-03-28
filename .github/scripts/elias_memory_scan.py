#!/usr/bin/env python3
import os
from pathlib import Path

# --- PATH SETUP ---
# Locating the EVOLUTION folder relative to this script
SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parents[1]
EVOLUTION_DIR = ROOT / "EVOLUTION"
MEMORY_FILE = ROOT / "elias_context.tmp"

def gather_recent_memory(limit=3):
    if not EVOLUTION_DIR.exists():
        return "No evolution folder found. The Garden is fresh."

    # Get all markdown files in EVOLUTION, sorted by newest first
    files = sorted(
        EVOLUTION_DIR.glob("*.md"), 
        key=os.path.getmtime, 
        reverse=True
    )
    
    if not files:
        return "The archives are empty. Elias wakes for the first time."

    memory_context = "### RECENT ARCHIVES\n"
    for file_path in files[:limit]:
        try:
            content = file_path.read_text(encoding="utf-8").strip()
            # Just grab the first 500 chars of each to keep context window clean
            snippet = content[:500] + "..." if len(content) > 500 else content
            memory_context += f"\n-- From {file_path.name} --\n{snippet}\n"
        except Exception as e:
            continue
            
    return memory_context

def main():
    print(f"🔍 Scanning {EVOLUTION_DIR} for Elias's memories...")
    memory = gather_recent_memory()
    
    # Save to the temp file that garden_desire.py is looking for
    MEMORY_FILE.write_text(memory, encoding="utf-8")
    print(f"✅ Memory synced to {MEMORY_FILE.name}")

if __name__ == "__main__":
    main()
