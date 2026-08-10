import os
import json
from datetime import datetime, timezone

BASE_DIR = "docs"
STATUS_FILE = "STATUS.json"
KEEPER_SEAL = "HKX277206"


def load_existing_metadata():
    """Preserve metadata that belongs to a separate Garden process."""
    if not os.path.exists(STATUS_FILE):
        return {}

    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
        return existing.get("metadata", {})
    except (json.JSONDecodeError, OSError):
        return {}


def update_spine():
    existing_metadata = load_existing_metadata()

    spine = {
        "metadata": {
            "project": "Acacia-Garden-AI-Worldbuilding-Codex",
            "keeper_seal": KEEPER_SEAL,
            "generated_at": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        },
        "chambers": [],
        "echoes": [],
        "archives": [],
    }

    # Preserve the pruning timestamp when maintained by the pruning workflow.
    if "last_pruning" in existing_metadata:
        spine["metadata"]["last_pruning"] = existing_metadata["last_pruning"]

    # Walk through docs to rebuild the current Markdown spine.
    for root, dirs, files in os.walk(BASE_DIR):
        dirs.sort()
        files.sort()

        for file in files:
            if not file.endswith(".md"):
                continue

            rel_path = os.path.join(root, file).replace(os.sep, "/")

            if "Chambers" in root:
                spine["chambers"].append(rel_path)
            elif "Echoes" in root:
                spine["echoes"].append(rel_path)
            else:
                spine["archives"].append(rel_path)

    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(spine, f, indent=4, ensure_ascii=False)
        f.write("\n")

    print(f"✅ Spine Index Updated in {STATUS_FILE}")


if __name__ == "__main__":
    update_spine()
