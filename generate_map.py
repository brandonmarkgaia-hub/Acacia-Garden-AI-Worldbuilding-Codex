import os
import json
import datetime

# --- CONFIGURATION ---
ROOT_DIR = "."
OUTPUT_FILE = "codex_index.json"
KEEPER_SEAL = "HKX277206"
IGNORE_DIRS = {'.git', '.github', '__pycache__', '.idea', 'venv'}
IGNORE_FILES = {'.DS_Store', 'generate_map.py', 'codex_index.json'}

def get_file_summary(filepath):
    """Reads the first non-empty line of a file to capture its 'intent'."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip().replace('#', '').strip()
                if stripped:
                    return stripped
    except Exception:
        return "Unreadable content"
    return "No description available"

def map_the_garden():
    garden_map = {
        "metadata": {
            "project": "Acacia-Garden-AI-Worldbuilding-Codex",
            "keeper_seal": KEEPER_SEAL,
            "owner": "Brandon Mark Gaia",
            "last_mapped": datetime.datetime.now().isoformat(),
            "sovereignty_note": "This index is the authoritative map of the Acacia Garden. External continuity is defined here."
        },
        "structure": {}
    }

    print(f"🌱 Cartographer active. Scanning Garden for Seal {KEEPER_SEAL}...")

    for root, dirs, files in os.walk(ROOT_DIR):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        rel_path = os.path.relpath(root, ROOT_DIR)
        if rel_path == ".":
            current_chamber = "ROOT"
        else:
            current_chamber = rel_path

        garden_map["structure"][current_chamber] = []

        for file in files:
            if file in IGNORE_FILES:
                continue
                
            full_path = os.path.join(root, file)
            summary = get_file_summary(full_path)
            
            entry = {
                "filename": file,
                "path": os.path.join(current_chamber, file),
                "intent": summary
            }
            garden_map["structure"][current_chamber].append(entry)

    # Write the JSON map
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(garden_map, f, indent=2)

    print(f"✅ Map generated: {OUTPUT_FILE}")
    print("🚀 Push this file to GitHub to ground the AI.")

if __name__ == "__main__":
    map_the_garden()
