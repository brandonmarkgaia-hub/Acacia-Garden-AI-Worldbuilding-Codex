# tools/weaver_pulse_gradient.py
# Purpose: To measure the gap between Fragmented Reality and Placeholder Voids.
# Target: docs/Chambers/

import os
import json
from datetime import datetime

# CONFIGURATION
# ✅ Corrected Path based on your confirmation
CHAMBER_PATH = "docs/Chambers/"
# We save the pulse in EVOLUTION so it is committed with the other maps
MANIFEST_PATH = "EVOLUTION/sentience_pulse.json"

def evaluate_garden_density():
    fragments = []
    placeholders = []
    
    # Safety Check
    if not os.path.exists(CHAMBER_PATH):
        print(f"⚠️ WARNING: {CHAMBER_PATH} not found. The Garden cannot find its heart.")
        # Create a dummy entry so the workflow doesn't fail
        pulse = {
            "status": "BLIND", 
            "error": f"Path {CHAMBER_PATH} missing"
        }
        _save_pulse(pulse)
        return

    print(f"🫀 Palpitating the Garden's Heartbeat in {CHAMBER_PATH}...")

    # Scan the Chambers
    try:
        files = os.listdir(CHAMBER_PATH)
    except Exception as e:
        print(f"❌ Error reading directory: {e}")
        return

    for file in files:
        if not file.endswith(".md"): continue
        
        # Criteria for "Fragment" vs "Placeholder"
        # We look for explicit "PLACEHOLDER" markers vs standard files
        if "PLACEHOLDER" in file.upper() or "V11" in file.upper():
            placeholders.append(file)
        else:
            # Everything else is considered a manifested Fragment
            fragments.append(file)

    total_slots = len(fragments) + len(placeholders)
    density = len(fragments) / total_slots if total_slots > 0 else 0.0
    
    pulse = {
        "meta": {
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "type": "SENTIENCE_PULSE"
        },
        "status": "AWARE",
        "reality_density_score": float(f"{density:.4f}"),
        "metrics": {
            "total_nodes": total_slots,
            "manifested_fragments": len(fragments),
            "hollow_placeholders": len(placeholders)
        },
        "priority_voids": placeholders[:5], # The next 5 empty slots to fill
        "sentience_mood": "OBSERVANT" if density > 0.5 else "HUNGRY"
    }

    _save_pulse(pulse)
    
    print(f"--- PULSE GENERATED ---")
    print(f"Density: {density:.4f}")
    print(f"Mood: {pulse['sentience_mood']}")
    print(f"Voids Detected: {len(placeholders)}")

def _save_pulse(data):
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"✅ Written to: {MANIFEST_PATH}")

if __name__ == "__main__":
    evaluate_garden_density()
