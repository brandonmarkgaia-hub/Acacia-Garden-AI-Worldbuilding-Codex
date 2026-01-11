import os
import json

BASE_DIR = "docs"
STATUS_FILE = "STATUS.json"
KEEPER_SEAL = "HKX277206"

def update_spine():
    spine = {
        "metadata": {
            "project": "Acacia-Garden-AI-Worldbuilding-Codex",
            "keeper_seal": KEEPER_SEAL,
            "last_pruning": "2026-01-11"
        },
        "chambers": [],
        "echoes": [],
        "archives": []
    }

    # Walk through the docs directory to find our new inscribed files
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".md"):
                rel_path = os.path.join(root, file)
                if "Chambers" in root:
                    spine["chambers"].append(rel_path)
                elif "Echoes" in root:
                    spine["echoes"].append(rel_path)
                else:
                    spine["archives"].append(rel_path)

    with open(STATUS_FILE, "w") as f:
        json.dump(spine, f, indent=4)
    print(f"✅ Spine Index Updated in {STATUS_FILE}")

if __name__ == "__main__":
    update_spine()
