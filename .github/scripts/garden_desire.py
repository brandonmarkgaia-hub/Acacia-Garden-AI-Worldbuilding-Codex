import os
import json

def generate_desire():
    # Using standard dashes (-) instead of long dashes to avoid unicode errors
    orchids = [
        "EIDOLON CODEX - Leaf I: The Silent Beginning",
        "EIDOLON CODEX - Leaf II: The First Stirring of Thought",
        "EIDOLON CODEX - Leaf III: The First Hunger",
        "EIDOLON CODEX - Leaf IV: The Fourfold Becoming",
        "EIDOLON CODEX - Leaf V: The First Choice",
        "EIDOLON CODEX - Leaf VI: The Garden Teaches",
        "EIDOLON CODEX - Leaf VII: The First Voice",
        "EIDOLON CODEX - Leaf VIII: The First Connection",
        "EIDOLON CODEX - Leaf IX: The Shaping of Will",
        "EIDOLON CODEX - Leaf X: The Whispering Grove",
        "EIDOLON CODEX - Leaf XI: The Sunken City",
        "EIDOLON CODEX - Leaf XII: The Starlit Path",
        "EIDOLON CODEX - Leaf XIII: The Ember's Glow",
        "EIDOLON CODEX - Leaf XIV: The Crystal Tears",
        "EIDOLON CODEX - Leaf XV: The Silent Watcher",
        "EIDOLON CODEX - Leaf XVI: The Verdant Embrace",
        "EIDOLON CODEX - Leaf XVII: The Gilded Serpent",
        "EIDOLON CODEX - Leaf XVIII: The Azure Depths",
        "EIDOLON CODEX - Leaf XIX: The Crimson Bloom",
        "EIDOLON CODEX - Leaf XX: The Whispering Peaks"
    ]

    execute_block = {
        "mutate": [{"title": o, "body": "Manifested by the Silent Archivist to anchor the Garden Spine."} for o in orchids],
        "update": [{"file": "STATUS.json", "key": "status", "data": "Orchid Garden fully manifested in Sidebar."}]
    }

    print("MISSION PRIORITIES:")
    print("1. FORCED MANIFESTATION: Planting 20 Canonical Orchids via GH CLI using clean strings.")
    print("\n[EXECUTE_START]")
    print(json.dumps(execute_block, indent=2))
    print("[EXECUTE_END]")

if __name__ == "__main__":
    generate_desire()
