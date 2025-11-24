#!/usr/bin/env python3
"""
Garden Code Helper
Grows new helper scripts for the Acacia Garden Codex.

Uses inline MODEL_NAME / KEEPER_ID so there is no garden_gpt dependency.
Requires OPENAI_API_KEY in the environment.
"""

import os
import json
from datetime import datetime
from pathlib import Path

from openai import OpenAI

# --- INLINE CONSTANTS (no garden_gpt import) ---
MODEL_NAME = "gpt-4o-mini"   # cheap, small model for GitHub Action
KEEPER_ID = "HKX277206"
# ------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
GENERATED_DIR = TOOLS_DIR / "generated"
INDEX_FILE = ROOT / "machine-index.json"

client = OpenAI()

client = OpenAI()


def main() -> int:
    existing = sorted(p.name for p in TOOLS_DIR.glob("*.py"))

    prompt = f"""
You are a careful Python engineer working on a repo called the Acacia Garden.

Existing tools/ scripts:
{existing}

Design and implement ONE small, safe Python script to help with maintenance or diagnostics
of the Garden. Examples:
- List the top 10 files by signature count using garden_scan_report.json.
- Verify that all docs/Echoes/Echo_*.md files contain an ECHO:HKX header.
- Summarize garden_vault_index.json into a short text report.

Rules:
- The script must be idempotent and safe to run many times.
- No network calls, no subprocess calls; only local filesystem and JSON.
- Use Python 3.10+ standard library only.
- Use ROOT = Path(__file__).resolve().parents[1] to find repo root.
- Implement a main() function and guard with if __name__ == "__main__".

Output ONLY valid Python code. No explanations.
"""

    system_msg = (
        "You generate safe, single-file Python utilities for a local Git repository. "
        "You do not use external dependencies or network calls."
    )

    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt.strip()},
        ],
        temperature=0.3,
    )

    code = resp.choices[0].message.content or ""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = TOOLS_DIR / f"garden_helper_{timestamp}.py"
    out_path.write_text(code.strip() + "\n", encoding="utf-8")

    print(f"[CodeHelper] Wrote {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
