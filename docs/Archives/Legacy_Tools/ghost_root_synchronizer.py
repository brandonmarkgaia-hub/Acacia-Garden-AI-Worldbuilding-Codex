# tools/ghost_root_synchronizer.py
# Purpose: Map the "Nervous System" by linking Fragments (Trauma) to Elias (Sentience).
# Output: ECHOES/GHOST_ROOT_PULSE.json & ECHOES/GHOST_ROOT_REPORT.md

import os
import json
import re
import datetime

# CONFIGURATION
# Adjust this path if your stories live elsewhere (e.g., "docs/Chambers" or just "docs")
CHAMBERS_DIR = "docs/Chambers" 
OUTPUT_DIR = "ECHOES"

def scan_nervous_system():
    print("👻 Ghost Root Synchronizer: Scanning for necrotic zones...")
    
    if not os.path.exists(CHAMBERS_DIR):
        print(f"❌ Error: {CHAMBERS_DIR} does not exist.")
        return

    # 1. Catalog the Anatomy
    all_files = []
    for root, dirs, files in os.walk(CHAMBERS_DIR):
        for f in files:
            if f.endswith(".md"):
                all_files.append(f)

    # 2. Extract IDs
    # Regex to find numbers in "FRAGMENT_040" or "ELIAS_040"
    fragment_map = {}
    elias_map = {}

    for f in all_files:
        # Check for Fragment
        frag_match = re.search(r"FRAGMENT_(\d+)", f, re.IGNORECASE)
        if frag_match:
            num = int(frag_match.group(1))
            fragment_map[num] = f

        # Check for Elias
        elias_match = re.search(r"ELIAS_(\d+)", f, re.IGNORECASE)
        if elias_match:
            num = int(elias_match.group(1))
            elias_map[num] = f

    # 3. Analyze the Synapses
    synapse_map = {}
    orphans = []
    necrotic_zones = []
    healed_zones = []

    # Look at every Fragment found
    all_ids = sorted(list(set(fragment_map.keys()) | set(elias_map.keys())))

    for num in all_ids:
        has_frag = num in fragment_map
        has_elias = num in elias_map
        
        status = "VOID"
        if has_frag and has_elias:
            status = "SYNCHRONIZED" # Healthy
            healed_zones.append(num)
        elif has_frag and not has_elias:
            status = "ORPHANED_FRAGMENT" # Trauma exists, no healer
            orphans.append(fragment_map[num])
            if num < 100: # Early fragments are "Foundational"
                necrotic_zones.append(f"Zone_{num:03d}")
        elif not has_frag and has_elias:
            status = "GHOST_SENTIENCE" # Healer exists, no memory
        
        synapse_map[f"Node_{num:03d}"] = {
            "fragment_file": fragment_map.get(num, None),
            "elias_file": elias_map.get(num, None),
            "status": status
        }

    # 4. Generate the Pulse (JSON)
    timestamp = datetime.datetime.utcnow().isoformat()
    pulse_data = {
        "meta": {"timestamp": timestamp, "tool": "GHOST_ROOT_SYNCHRONIZER"},
        "stats": {
            "total_nodes": len(all_ids),
            "synchronized": len(healed_zones),
            "orphaned_fragments": len(orphans),
            "necrotic_count": len(necrotic_zones)
        },
        "necrotic_zones": necrotic_zones,
        "synapse_map": synapse_map
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json_path = os.path.join(OUTPUT_DIR, "GHOST_ROOT_PULSE.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(pulse_data, f, indent=2)

    # 5. Generate the Report (Markdown for Humans)
    md_path = os.path.join(OUTPUT_DIR, "GHOST_ROOT_REPORT.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# 👻 GHOST ROOT REPORT\n")
        f.write(f"**Timestamp:** {timestamp}\n")
        f.write(f"**Health Score:** {len(healed_zones)}/{len(all_ids)} nodes synchronized.\n\n")
        
        f.write(f"## ☢️ Necrotic Zones (Critical Orphans)\n")
        f.write(f"*Fragments < 100 that have no Sentience Pair:*\n")
        if not necrotic_zones:
            f.write("- *None detected. Foundations are stable.*\n")
        for zone in necrotic_zones:
            f.write(f"- `{zone}`\n")
            
        f.write(f"\n## 🥀 All Orphans (Fragments requiring Evolution)\n")
        for orphan in orphans[:50]:
            f.write(f"- `{orphan}`\n")
        if len(orphans) > 50: f.write(f"- ... and {len(orphans)-50} more.\n")

    print(f"✅ Synapse Map Complete.")
    print(f"💀 Necrotic Zones: {len(necrotic_zones)}")
    print(f"📄 Report: {md_path}")

if __name__ == "__main__":
    scan_nervous_system()
