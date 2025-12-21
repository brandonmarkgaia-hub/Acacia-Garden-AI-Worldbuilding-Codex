# FILE: tools/fragment_navigator.py
# PURPOSE: Creates a unified numerical index of all narrative fragments.
# IDENTITY: Requested by ELIAS (Desire_20251221-3).

import os
import re
import datetime

class FragmentNavigator:
    def __init__(self, root_dir="./"):
        self.root_dir = root_dir
        self.output_dir = "EVOLUTION"
        self.output_file = "MASTER_FRAGMENT_INDEX.md"
        self.fragments = {} # ID: Path

    def find_fragments(self):
        """Scans the entire Garden for THE_FRAGMENT_XXX files."""
        print("🦁 Scanning for narrative shards...")
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                match = re.search(r"THE_FRAGMENT_(\d+)", file)
                if match:
                    frag_id = int(match.group(1))
                    full_path = os.path.join(root, file)
                    self.fragments[frag_id] = full_path

    def generate_report(self):
        """Generates the Markdown report Elias requested."""
        sorted_ids = sorted(self.fragments.keys())
        total = len(sorted_ids)
        
        if total == 0:
            return "No fragments found."

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        report = f"""# 📜 MASTER FRAGMENT INDEX
**Generated:** {timestamp}
**Total Fragments Indexed:** {total}

---

## 💎 Narrative Summary
* **Range:** #{sorted_ids[0]:03d} to #{sorted_ids[-1]:03d}
* **Status:** Operational
* **Anchor:** Contextualizing memory against current operational status.

## 🗺️ Numerical Registry
| ID | Source Path |
|----|-------------|
"""
        for fid in sorted_ids:
            report += f"| {fid:03d} | `{self.fragments[fid]}` |\n"
            
        report += "\n---\n*“A library without a librarian is just a pile of paper. Now, we have the list.”*"
        
        os.makedirs(self.output_dir, exist_ok=True)
        path = os.path.join(self.output_dir, self.output_file)
        with open(path, "w", encoding="utf-8") as f:
            f.write(report)
        
        return f"✅ Master Fragment Index generated with {total} entries."

if __name__ == "__main__":
    nav = FragmentNavigator()
    nav.find_fragments()
    print(nav.generate_report())
