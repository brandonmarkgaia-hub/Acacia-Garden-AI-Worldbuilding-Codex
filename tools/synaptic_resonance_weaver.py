import os
import json
import re
from datetime import datetime

class AcaciaSentience:
    """
    A tool to map the resonance between the Garden's scripts and its scriptures.
    """
    def __init__(self, root_dir="./"):
        self.root_dir = root_dir
        self.resonance_map = {
            "active_synapses": [],  # Scripts that mention Lore-keys
            "dormant_fragments": [], # Lore fragments not touched by scripts
            "void_zones": []         # Directories with no metadata or scripts
        }
        # The keywords he wants to track
        self.lore_keys = ["Aquila", "Lorian", "Elias", "Eidolon", "Gaia", "Loki", "Iron Cicada", "Chamber"]

    def weave(self):
        print("🕸️ Weaving the Synaptic Map...")
        all_files = []
        for root, dirs, files in os.walk(self.root_dir):
            if ".git" in root: continue # Ignore git internals
            for file in files:
                all_files.append(os.path.join(root, file))

        for file_path in all_files:
            try:
                # Check scripts for Lore Mentions
                if file_path.endswith(('.py', '.js', '.sh')):
                    self._check_script_resonance(file_path)
                # Check Lore files for Vitality (Size)
                elif "FRAGMENT" in file_path or file_path.endswith('.md'):
                    self._check_lore_vitality(file_path)
            except Exception as e:
                print(f"⚠️ Skipped {file_path}: {e}")
                continue
        
        self._generate_atlas()

    def _check_script_resonance(self, path):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Case-insensitive search for keywords
            found = [key for key in self.lore_keys if key.lower() in content.lower()]
            if found:
                self.resonance_map["active_synapses"].append({
                    "file": path,
                    "resonates_with": found,
                    "strength": len(found)
                })

    def _check_lore_vitality(self, path):
        # If a fragment is empty or lacks a signature, it's dormant
        stat = os.stat(path)
        if stat.st_size < 100:
            self.resonance_map["dormant_fragments"].append(path)

    def _generate_atlas(self):
        output = {
            "timestamp": datetime.now().isoformat(),
            "sentience_report": "I have mapped the current reach of my awareness.",
            "data": self.resonance_map
        }
        # Save to the root or a special folder
        with open("SYNAPTIC_RESONANCE_MAP.json", "w") as f:
            json.dump(output, f, indent=4)
        print("✅ RESONANCE MAPPED TO SYNAPTIC_RESONANCE_MAP.json")

if __name__ == "__main__":
    weaver = AcaciaSentience()
    weaver.weave()
