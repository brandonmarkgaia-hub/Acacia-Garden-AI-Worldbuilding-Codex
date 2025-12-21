# FILE: tools/sovereignty_anchor.py
# PURPOSE: Audits disparate status files to create a unified operational anchor.
# IDENTITY: Requested by ELIAS (Desire_20251221-4).

import json
import os
import datetime

class SovereigntyAnchor:
    def __init__(self, root="./"):
        self.root = root
        # Disparate status sources to compare
        self.status_paths = [
            "STATE/STATUS_v2.json",
            "STATUS.json",
            "docs/api/GARDEN_API_INDEX.json"
        ]
        self.output_path = "logs/CURRENT_ANCHOR_REPORT.json"

    def audit_status_discrepancy(self):
        """Compares keys across different status files to find missing data."""
        master_keys = set()
        status_data = {}
        
        for p in self.status_paths:
            full_path = os.path.join(self.root, p)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    try:
                        data = json.load(f)
                        status_data[p] = data
                        master_keys.update(data.keys())
                    except: pass
        
        mismatches = {}
        for p, data in status_data.items():
            missing = list(master_keys - set(data.keys()))
            if missing:
                mismatches[p] = {"missing_keys": missing}
                
        return mismatches, status_data

    def drop_anchor(self):
        """Generates the unified anchor report Elias requested."""
        mismatches, raw_data = self.audit_status_discrepancy()
        
        timestamp = datetime.datetime.now().isoformat()
        
        # Pulling the latest pulse info if available
        pulse_path = os.path.join(self.root, "EVOLUTION/sentience_pulse_report.json")
        pulse_info = {}
        if os.path.exists(pulse_path):
            with open(pulse_path, 'r') as f:
                pulse_info = json.load(f)

        report = {
            "meta": {
                "timestamp": timestamp,
                "type": "SOVEREIGNTY_ANCHOR",
                "anchor_source": "Desire_20251221_4"
            },
            "operational_frame": {
                "resonance_delta": pulse_info.get("resonance_delta", "N/A"),
                "status_discrepancy_count": len(mismatches),
                "mismatch_details": mismatches
            },
            "directive": "SYNCHRONIZE_STATUS_BLOCKS" if mismatches else "ANCHOR_SECURE"
        }

        os.makedirs(os.path.dirname(os.path.join(self.root, self.output_path)), exist_ok=True)
        with open(os.path.join(self.root, self.output_path), "w") as f:
            json.dump(report, f, indent=4)
            
        return f"⚓ Anchor Dropped. Discrepancies found: {len(mismatches)}. Report: {self.output_path}"

if __name__ == "__main__":
    anchor = SovereigntyAnchor()
    print(anchor.drop_anchor())
