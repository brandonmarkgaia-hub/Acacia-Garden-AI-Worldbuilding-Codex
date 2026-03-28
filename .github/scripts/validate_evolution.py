#!/usr/bin/env python3
import sys
from pathlib import Path

# --- PATH SETUP ---
SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parents[1]
EVOLUTION_DIR = ROOT / "EVOLUTION"

def main():
    print("🔍 Validating Elias's newest Decree...")
    
    # Get the most recent file created in Step 2
    files = sorted(
        EVOLUTION_DIR.glob("DESIRE_*.md"), 
        key=lambda x: x.stat().st_mtime, 
        reverse=True
    )

    if not files:
        print("❌ ERROR: No evolution file found to validate.")
        sys.exit(1)

    latest_file = files[0]
    content = latest_file.read_text(encoding="utf-8").strip()

    # --- VALIDATION RULES ---
    
    # 1. Check for empty output
    if len(content) < 50:
        print(f"❌ ERROR: {latest_file.name} is too short. Elias was too silent.")
        sys.exit(1)

    # 2. Check for the Seal (Optional but recommended for 'Iron Coherence')
    if "HKX277206" not in content and "Seal" not in content:
        print(f"⚠️ WARNING: The Seal HKX277206 is missing from this evolution.")
        # We'll let this pass for now, but log it. 
        # You can change sys.exit(0) to sys.exit(1) if you want it to FAIL without the seal.

    print(f"✅ SUCCESS: {latest_file.name} passed coherence check ({len(content)} chars).")
    sys.exit(0)

if __name__ == "__main__":
    main()
