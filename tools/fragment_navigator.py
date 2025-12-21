# FILE: tools/fragment_navigator.py
# PURPOSE: Unified Indexing and Prioritization of Narrative Fragments.
# IDENTITY: Fulfills Desires 3, 10, and 11 for ELIAS.

import os
import re
import json
import datetime
from pathlib import Path

class FragmentNavigator:
    def __init__(self, root="."):
        self.root = Path(root)
        self.output_dir = self.root / "EVOLUTION"
        self.md_index_path = self.output_dir / "MASTER_FRAGMENT_INDEX.md"
        self.json_queue_path = self.output_dir / "PRIORITY_QUEUE_STATUS.json"
        self.fragments = {} # ID: Path

    def find_fragments(self):
        """Scans the Garden for THE_FRAGMENT_XXX files."""
        print("🦁 Scanning for narrative shards...")
        for root, _, files in os.walk(self.root):
            for file in files:
                match = re.search(r"THE_FRAGMENT_(\d+)", file)
                if match:
                    frag_id = int(match.group(1))
                    self.fragments[frag_id] = os.path.join(root, file)

    def infer_nexus(self, content):
        """Determines the 'Nexus' of a fragment based on Desire 11."""
        content_up = content.upper()
        if "ELIAS" in content_up: return "ACTIVE_SENTIENCE"
        if "AQUILA" in content_up or "PROTOCOL" in content_up: return "PROTOCOL_CORE"
        if "VOID" in content_up: return "GAP_ANALYSIS"
        return "STAGNANT"

    def generate_outputs(self):
        """Generates both the MD Index and the JSON Priority Queue."""
        sorted_ids = sorted(self.fragments.keys())
        if not sorted_ids:
            return "No fragments found."

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # --- 1. GENERATE MASTER_FRAGMENT_INDEX.md (Desire 3) ---
        report_md = f"# 📜 MASTER FRAGMENT INDEX\n**Generated:** {timestamp}\n**Total:** {len(sorted_ids)}\n\n| ID | Path |\n|----|------|\n"
        
        # --- 2. GENERATE PRIORITY_QUEUE_STATUS.json (Desire 11) ---
        queue_data = []
        
        for fid in sorted_ids:
            path = self.fragments[fid]
            report_md += f"| {fid:03d} | `{path}` |\n"
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            nexus = self.infer_nexus(content)
            queue_data.append({
                "id": f"{fid:03d}",
                "nexus": nexus,
                "priority": 1 if nexus != "STAGNANT" else 3,
                "path": path
            })

        # Save MD
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.md_index_path, "w", encoding="utf-8") as f:
            f.write(report_md)
            
        # Save JSON
        with open(self.json_queue_path, "w", encoding="utf-8") as f:
            json.dump({"meta": "FRAGMENT_PRIORITIZATION_QUEUE", "timestamp": timestamp, "queue": queue_data}, f, indent=4)
        
        return f"✅ Unified Navigation Complete.\n- Index: {self.md_index_path}\n- Queue: {self.json_queue_path}"

if __name__ == "__main__":
    nav = FragmentNavigator()
    nav.find_fragments()
    print(nav.generate_outputs())
