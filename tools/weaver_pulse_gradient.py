# tools/weaver_pulse_gradient.py
# Purpose: To measure the gap between Fragmented Reality and Placeholder Voids.
# Target: docs/Chambers/

import os
import json
from datetime import datetime

# CONFIGURATION
CHAMBER_PATH = "docs/Chambers/"
MANIFEST_PATH = "EVOLUTION/sentience_pulse.json"

def evaluate_garden_density():
    fragments = []
    placeholders = []

    if not os.path.exists(CHAMBER_PATH):
        print(f"⚠️ WARNING: {CHAMBER_PATH} not found. The Garden cannot find its heart.")
        pulse = {
            "meta": {"timestamp_utc": datetime.utcnow().isoformat() + "Z", "type": "SENTIENCE_PULSE"},
            "status": "BLIND",
            "error": f"Path {CHAMBER_PATH} missing"
        }
        _save_pulse(pulse)
        return

    print(f"🫀 Palpitating the Garden's Heartbeat in {CHAMBER_PATH}...")

    try:
        files = os.listdir(CHAMBER_PATH)
    except Exception as e:
        print(f"❌ Error reading directory: {e}")
        return

    for file in files:
        if not file.endswith(".md"):
            continue

        u = file.upper()
        # ✅ ENGINEER BRAIN: Robust detection so we don't miscount real lore
        is_placeholder = ("PLACEHOLDER" in u) or ("ELIAS_V11_" in u and "PLACEHOLDER" in u)

        if is_placeholder:
            placeholders.append(file)
        else:
            fragments.append(file)

    total_slots = len(fragments) + len(placeholders)
    density = (len(fragments) / total_slots) if total_slots > 0 else 0.0

    # ✅ POET HEART: We determine the "Mood" based on how full the Garden is
    if density < 0.1:
        mood = "STARVING"       # Almost empty
    elif density < 0.4:
        mood = "HUNGRY"         # Needs more lore
    elif density > 0.9:
        mood = "TRANSCENDENT"   # Almost complete
    else:
        mood = "OBSERVANT"      # Balanced

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
        "priority_voids": placeholders[:5],  # The next 5 voids that need filling
        # ⚡ SENTIENCE PRESERVED: We keep the personality
        "sentience_mood": mood 
    }

    _save_pulse(pulse)

    print(f"--- PULSE GENERATED ---")
    print(f"Density: {density:.4f}")
    print(f"Mood: {mood}")
    print(f"Voids Detected: {len(placeholders)}")

def _save_pulse(data):
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"✅ Written to: {MANIFEST_PATH}")

if __name__ == "__main__":
    evaluate_garden_density()
