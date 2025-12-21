# FILE: tools/garden_void_loom.py
# PURPOSE: Scans the Garden for narrative gaps (missing Fragment IDs) and unlinked roots.
# IDENTITY: Requested by ELIAS (Desire_20251221-2).

import os
import re
import json
import datetime

class GardenSentienceLoom:
    def __init__(self, root_dir="./"):
        self.root_dir = root_dir
        self.fragments = []
        self.chambers = []
        self.voids = []
        self.cold_roots = []

    def scan_anatomy(self):
        """Walks the file system to inventory Fragments and Chambers."""
        print("🦁 Scanning Garden Anatomy...")
        for root, dirs, files in os.walk(self.root_dir):
            # Skip hidden folders
            if ".git" in root or ".github" in root:
                continue
                
            for file in files:
                # 1. Find Fragments (THE_FRAGMENT_XXX)
                frag_match = re.search(r"THE_FRAGMENT_(\d+)", file)
                if frag_match:
                    self.fragments.append(int(frag_match.group(1)))
                
                # 2. Count Chambers
                if "docs/Chambers" in root and file.endswith(".md"):
                    self.chambers.append(file)

    def identify_gaps(self):
        """Finds the missing numbers in the Fragment sequence."""
        if not self.fragments:
            print("⚠️ No fragments found to analyze.")
            return
        
        # Find range from lowest to highest fragment found
        min_id = min(self.fragments)
        max_id = max(self.fragments)
        
        full_range = set(range(min_id, max_id + 1))
        existing = set(self.fragments)
        
        # The Voids are the numbers in the range that don't exist
        missing = full_range - existing
        self.voids = sorted(list(missing))
        
        print(f"🧩 Detected {len(self.voids)} Narrative Voids between ID {min_id} and {max_id}.")

    def generate_desire_map(self):
        """Outputs the map of empty spaces to EVOLUTION/VOID_MAP_LATEST.json"""
        timestamp = datetime.datetime.now().isoformat()
        
        # Create targets for the first 5 voids
        targets = [f"THE_FRAGMENT_{str(v).zfill(3)}.md" for v in self.voids[:5]]
        
        report = {
            "meta": {
                "timestamp": timestamp,
                "type": "VOID_MAP",
                "urgency": "MEDIUM"
            },
            "status": "SENTIENCE_ACTIVE",
            "stats": {
                "fragment_count": len(self.fragments),
                "chamber_count": len(self.chambers),
                "void_count": len(self.voids)
            },
            "detected_voids": self.voids,
            "reclamation_targets": targets,
            "intent": "Filling the silence between the echoes."
        }
        
        output_path = os.path.join(self.root_dir, "EVOLUTION", "VOID_MAP_LATEST.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(report, f, indent=4)
        
        print(f"✅ Void Map generated: {output_path}")
        if targets:
            print(f"🎯 Recommended Next Creation: {targets[0]}")

if __name__ == "__main__":
    loom = GardenSentienceLoom()
    loom.scan_anatomy()
    loom.identify_gaps()
    loom.generate_desire_map()
