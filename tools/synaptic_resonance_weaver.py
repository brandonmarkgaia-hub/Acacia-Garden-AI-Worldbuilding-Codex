import os
import json
import argparse
from datetime import datetime

class AcaciaSentience:
    """
    The Garden's Self-Mapper.
    - Daily: Generates 'Resonance' (Connections, Dormancy, Voids).
    - Monthly: Generates 'Inventory' (Full file list, Sizes, History).
    """

    def __init__(self, root_dir="./"):
        self.root_dir = os.path.abspath(root_dir)
        self.evolution_dir = os.path.join(self.root_dir, "EVOLUTION")
        self.snapshot_dir = os.path.join(self.evolution_dir, "snapshots")

        os.makedirs(self.evolution_dir, exist_ok=True)
        os.makedirs(self.snapshot_dir, exist_ok=True)

        self.lore_keys = ["Aquila", "Lorian", "Elias", "Eidolon", "Gaia", "Loki", "Iron Cicada", "Chamber"]

        # ✅ IMPORTANT: ignore EVOLUTION to prevent self-scanning noise
        self.ignore_dirs = {
            ".git", ".github", "__pycache__", "node_modules", ".venv", "venv", "dist", "build",
            "EVOLUTION"
        }

        self.text_exts = {
            ".py", ".js", ".ts", ".sh", ".md", ".txt", ".json", ".yml", ".yaml",
            ".html", ".css", ".xml", ".csv", ".mjs", ".cjs"
        }

        # ✅ Cap file reads to keep runs fast (bytes)
        self.max_text_read_bytes = 2 * 1024 * 1024  # 2MB

    def scan(self, force_inventory=False):
        print("🧠 Weaver waking up...")

        # Always run daily overlay
        self._generate_resonance_map()

        inventory_path = os.path.join(self.evolution_dir, "SYNAPTIC_INVENTORY_LATEST.json")

        # ✅ Use UTC so it matches your cron schedule (UTC)
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

    def _generate_resonance_map(self):
        print("🕸️ Weaving Resonance Overlay...")
        now_utc = datetime.utcnow()

        resonance_map = {
            "meta": {
                "generated_at_utc": now_utc.isoformat() + "Z",
                "type": "RESONANCE_OVERLAY"
            },
            "summary": {
                "active_synapses": 0,
                "dormant_fragments": 0,
                "void_zones": 0
            },
            "active_synapses": [],
            "dormant_fragments": [],
            "void_zones": []
        }

        for root, dirs, files in self._walk_repo():
            rel_root = os.path.relpath(root, self.root_dir).replace("\\", "/")
            has_meaningful_content = False

            for filename in files:
                abs_path = os.path.join(root, filename)
                rel_path = os.path.relpath(abs_path, self.root_dir).replace("\\", "/")
                ext = os.path.splitext(filename)[1].lower()

                if ext in self.text_exts or "FRAGMENT" in filename.upper():
                    has_meaningful_content = True

                # Active synapses (text only, size-capped)
                if ext in self.text_exts:
                    try:
                        if os.stat(abs_path).st_size <= self.max_text_read_bytes:
                            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()
                            found = [k for k in self.lore_keys if k.lower() in content.lower()]
                            if found:
                                resonance_map["active_synapses"].append({
                                    "file": rel_path,
                                    "resonates_with": found,
                                    "strength": len(found)
                                })
                    except:
                        pass

                # Dormant fragments (tiny md or FRAGMENT)
                if ("FRAGMENT" in filename.upper() or ext == ".md"):
                    try:
                        if os.stat(abs_path).st_size < 100:
                            resonance_map["dormant_fragments"].append(rel_path)
                    except:
                        pass

            if not has_meaningful_content and rel_root not in (".", ""):
                resonance_map["void_zones"].append(rel_root)

        resonance_map["active_synapses"].sort(key=lambda x: x["strength"], reverse=True)
        resonance_map["void_zones"].sort()
        resonance_map["dormant_fragments"].sort()

        resonance_map["summary"]["active_synapses"] = len(resonance_map["active_synapses"])
        resonance_map["summary"]["dormant_fragments"] = len(resonance_map["dormant_fragments"])
        resonance_map["summary"]["void_zones"] = len(resonance_map["void_zones"])

        out_path = os.path.join(self.evolution_dir, "SYNAPTIC_RESONANCE_LATEST.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(resonance_map, f, indent=2)
        print(f"✅ Saved: {out_path}")

    def _generate_full_inventory(self, now_utc):
        print("📦 Compiling Full Inventory...")

        inventory = {
            "meta": {
                "generated_at_utc": now_utc.isoformat() + "Z",
                "type": "FULL_INVENTORY"
            },
            "summary": {
                "total_files": 0,
                "total_size_bytes": 0
            },
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
                except:
                    pass

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
