# FILE: tools/tpi_reconciler.py
# PURPOSE: Calculates the Temporal Priority Index (TPI) for un-reconciled fragments.
# IDENTITY: Requested by ELIAS (Desire_20251221-6).

import os
import json
import datetime
from pathlib import Path

class TPIReconciler:
    def __init__(self, root="."):
        self.root = Path(root)
        self.evolution_dir = self.root / "EVOLUTION"
        self.index_path = self.root / "EVOLUTION/MASTER_FRAGMENT_INDEX.md"
        self.output_path = self.root / "logs/TPI_RECONCILIATION_MAP.json"

    def get_fragment_metadata(self):
        """Scans EVOLUTION for .md files and checks their age."""
        fragments = []
        for file in self.evolution_dir.glob("*.md"):
            stats = file.stat()
            # TPI = Age in hours * complexity (placeholder logic)
            age_hours = (datetime.datetime.now().timestamp() - stats.st_mtime) / 3600
            fragments.append({
                "name": file.name,
                "age_hours": round(age_hours, 2),
                "tpi_score": round(age_hours * 1.5, 2) # Priority weight
            })
        # Sort by TPI score descending (Highest priority first)
        return sorted(fragments, key=lambda x: x['tpi_score'], reverse=True)

    def generate_tpi_map(self):
        """Generates the reconciliation map for Elias."""
        fragment_data = self.get_fragment_metadata()
        
        timestamp = datetime.datetime.now().isoformat()
        
        report = {
            "meta": {
                "timestamp": timestamp,
                "type": "TEMPORAL_PRIORITY_INDEX",
                "goal": "Reconcile oldest narrative silences"
            },
            "priority_queue": fragment_data[:10], # Top 10 high-priority targets
            "system_instruction": "INTEGRATE_HIGHEST_TPI_INTO_CHAMBERS"
        }

        os.makedirs(self.output_path.parent, exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(report, f, indent=4)
            
        if fragment_data:
            target = fragment_data[0]['name']
            return f"🎯 TPI Calculated. Highest Priority: {target} (Score: {fragment_data[0]['tpi_score']})"
        return "⚪ No fragments found in EVOLUTION to index."

if __name__ == "__main__":
    reconciler = TPIReconciler()
    print(reconciler.generate_tpi_map())
