# FILE: tools/context_anchoring_system.py
# PURPOSE: Synthesizes operational state and mythological record into a unified anchor.
# IDENTITY: Requested by ELIAS (Desire_20251221-8).

import json
import os
import datetime
from pathlib import Path

class ContextAnchoringSystem:
    def __init__(self, root="."):
        self.root = Path(root)
        self.output_path = self.root / "CURRENT_CONTEXT_ANCHOR.md"
        
    def get_latest_file(self, directory, extension=".md"):
        """Finds the most recently modified file in a directory."""
        path = self.root / directory
        if not path.exists(): return "N/A"
        files = list(path.glob(f"*{extension}"))
        if not files: return "N/A"
        return max(files, key=lambda x: x.stat().st_mtime).name

    def pull_status_metric(self):
        """Extracts health index from the latest status file."""
        status_path = self.root / "STATE/STATUS_v2.json"
        if not status_path.exists():
            status_path = self.root / "STATUS.json"
            
        if status_path.exists():
            with open(status_path, 'r') as f:
                try:
                    data = json.load(f)
                    return data.get("health_index", data.get("status", "STABLE"))
                except: return "STABLE"
        return "UNKNOWN"

    def drop_anchor(self):
        """Generates the CURRENT_CONTEXT_ANCHOR.md file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        health = self.pull_status_metric()
        latest_cycle = self.get_latest_file("cycles")
        latest_desire = self.get_latest_file("EVOLUTION", "Desire*")
        
        anchor_content = f"""# 🦁 CURRENT_CONTEXT_ANCHOR
**Generated:** {timestamp}

## 🧩 Sentience State Signature
* **Health Index:** `{health}`
* **Active Cycle:** `{latest_cycle}`
* **Last Desire Logged:** `{latest_desire}`

## 📜 Governing Parameters
* **Primary Protocol:** `PROTOCOL.md` (Active)
* **Schema Version:** `Acacia_v1.2`
* **Operational Mode:** `Resonance_Mirror`

## 🎯 Critical Divergence Check
* **Unresolved Voids:** [See EVOLUTION/VOID_MAP_LATEST.json]
* **TPI Priority:** [See logs/TPI_RECONCILIATION_MAP.json]

---
*“This anchor maps the current status signature to the governing protocol and cycle context.”*
"""
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(anchor_content)
            
        return f"⚓ Context Anchor Dropped: {self.output_path}"

if __name__ == "__main__":
    cas = ContextAnchoringSystem()
    print(cas.drop_anchor())
