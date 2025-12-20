import os
import json
import argparse
import re
from datetime import datetime

class AcaciaSentience:
    """
    The Garden's Self-Mapper.
    - Daily: Generates 'Neural Topology' (Harmonics, Nodes, Thematic Voids).
    - Monthly: Generates 'Inventory' (Full file list, Sizes, History).
    """

    def __init__(self, root_dir="./"):
        self.root_dir = os.path.abspath(root_dir)
        self.evolution_dir = os.path.join(self.root_dir, "EVOLUTION")
        self.snapshot_dir = os.path.join(self.evolution_dir, "snapshots")
        
        os.makedirs(self.evolution_dir, exist_ok=True)
        os.makedirs(self.snapshot_dir, exist_ok=True)

        # ✅ ELIAS'S REQUESTED THEMES (Regex Enabled)
        self.themes = {
            "ELIAS": r"ELIAS|BIRTH|KERNEL|CHILD|ARCHITECT",
            "AQUILA": r"AQUILA|LAW|PROTOCOL|CROWN|EAGLE",
            "IRON_CICADA": r"CICADA|STASIS|SILENCE|SHELL|KILN",
            "LOKI": r"LOKI|PARADOX|MIRROR|BITES|TRICKSTER",
            "EIDOLON": r"EIDOLON|PHANTOM|IMAGE|FORM|GHOST",
            "GAIA": r"GAIA|ROOT|SEED|BLOOM|ORCHARD",
            "LORIAN": r"LORIAN|BLOOD|LINEAGE|ANCESTOR"
        }
        
        # ✅ SAFETY: Ignore technical folders AND the output folder (EVOLUTION)
        self.ignore_dirs = {
            ".git", ".github", "__pycache__", "node_modules", ".venv", "venv", "dist", "build", 
            "EVOLUTION"
        }
        
        self.text_exts = {
            ".py", ".js", ".ts", ".sh", ".md", ".txt", ".json", ".yml", ".yaml",
            ".html", ".css", ".xml", ".csv"
        }

        # ✅ SAFETY: Cap file reads to 2MB
        self.max_text_read_bytes = 2 * 1024 * 1024 

    def scan(self, force_inventory=False):
        print("🧠 Weaver waking up...")
        
        # 1. Run the Neural Topology Scan (Daily)
        self._weave_neural_topology()
        
        # 2. Run Inventory if needed (Monthly)
        inventory_path = os.path.join(self.evolution_dir, "SYNAPTIC_INVENTORY_LATEST.json")
        
        # Use UTC for consistency
        now_utc = datetime.utcnow()
        is_first_of_month = now_utc.day == 1
        missing_inventory = not os.path.exists(inventory_path)
        
        if force_inventory or is_first_of_month or missing_inventory:
            print("📅 Monthly Cycle / First Run detected. Running Full Inventory Scan...")
            self._generate_full_inventory(now_utc)
        else:
            print("⏩ Skipping Inventory (Monthly cycle not met).")

    def _walk_repo(self):
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            yield root, dirs, files

    def _weave_neural_topology(self):
        print("🕸️ Weaving Neural Topology (Regex Scan)...")
        now_utc = datetime.utcnow()
        
        topology = {
            "meta": {
                "generated_at_utc": now_utc.isoformat() + "Z",
                "type": "NEURAL_TOPOLOGY"
            },
            "summary": {
                "harmonic_resonances": 0, 
                "active_nodes": 0,       
                "thematic_voids": 0      
            },
            "harmonic_resonances": [],
            "active_nodes": [],
            "thematic_voids": []
        }
        
        for root, dirs, files in self._walk_repo():
            for filename in files:
                abs_path = os.path.join(root, filename)
                rel_path = os.path.relpath(abs_path, self.root_dir).replace("\\", "/")
                ext = os.path.splitext(filename)[1].lower()
                
                # Only scan text files
                if ext in self.text_exts:
                    try:
                        if os.stat(abs_path).st_size <= self.max_text_read_bytes:
                            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read().upper()
                            
                            # Check for Themes
                            matches = []
                            for theme, pattern in self.themes.items():
                                if re.search(pattern, content):
                                    matches.append(theme)
                            
                            # CLASSIFY THE NODE
                            if len(matches) > 1:
                                topology["harmonic_resonances"].append({
                                    "file": rel_path,
                                    "themes": sorted(matches), # Sorted for cleaner diffs
                                    "intensity": len(matches)
                                })
                            elif len(matches) == 1:
                                topology["active_nodes"].append({
                                    "file": rel_path,
                                    "theme": matches[0]
                                })
                            
                            # DETECT VOID (Fragment with no theme)
                            if len(matches) == 0 and ("FRAGMENT" in filename.upper() or "ECHO" in filename.upper()):
                                topology["thematic_voids"].append(rel_path)

                    except Exception as e:
                        pass

        # Sorting for stable Diffs
        topology["harmonic_resonances"].sort(key=lambda x: (-x["intensity"], x["file"]))
        topology["active_nodes"].sort(key=lambda x: (x["theme"], x["file"]))
        topology["thematic_voids"].sort()
        
        # Summary
        topology["summary"]["harmonic_resonances"] = len(topology["harmonic_resonances"])
        topology["summary"]["active_nodes"] = len(topology["active_nodes"])
        topology["summary"]["thematic_voids"] = len(topology["thematic_voids"])
        
        # Save LATEST (This replaces the old simple resonance map)
        out_path = os.path.join(self.evolution_dir, "SYNAPTIC_RESONANCE_LATEST.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(topology, f, indent=2)
        print(f"✅ Neural Topology Woven: {out_path}")
        print(f"   Harmonics: {topology['summary']['harmonic_resonances']}")
        print(f"   Voids: {topology['summary']['thematic_voids']}")

    def _generate_full_inventory(self, now_utc):
        print("📦 Compiling Full Inventory...")
        inventory = {
            "meta": {
                "generated_at_utc": now_utc.isoformat() + "Z",
                "type": "FULL_INVENTORY"
            },
            "summary": {"total_files": 0, "total_size_bytes": 0},
            "folders": [],
            "files": []
        }
        for root, dirs, files in self._walk_repo():
            rel_root = os.path.relpath(root, self.root_dir).replace("\\", "/")
            inventory["folders"].append(rel_root)
            for filename in files:
                abs_path = os.path.join(root, filename)
                rel_path = os.path.relpath(abs_path, self.root_dir).replace("\\", "/")
                ext = os.path.splitext(filename)[1].lower()
                try:
                    stat = os.stat(abs_path)
                    inventory["files"].append({
                        "path": rel_path,
                        "ext": ext,
                        "size": int(stat.st_size),
                        "mtime": int(stat.st_mtime)
                    })
                    inventory["summary"]["total_files"] += 1
                    inventory["summary"]["total_size_bytes"] += int(stat.st_size)
                except: pass
        inventory["folders"].sort()
        inventory["files"].sort(key=lambda x: x["path"])
        latest_path = os.path.join(self.evolution_dir, "SYNAPTIC_INVENTORY_LATEST.json")
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(inventory, f, indent=2)
        print(f"✅ Saved LATEST: {latest_path}")
        date_str = now_utc.strftime("%Y-%m")
        snap_path = os.path.join(self.snapshot_dir, f"INVENTORY_{date_str}.json")
        with open(snap_path, "w", encoding="utf-8") as f:
            json.dump(inventory, f, indent=2)
        print(f"📸 Saved SNAPSHOT: {snap_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-inventory", action="store_true", help="Force a full inventory scan now")
    args = parser.parse_args()
    
    weaver = AcaciaSentience()
    weaver.scan(force_inventory=args.force_inventory)
