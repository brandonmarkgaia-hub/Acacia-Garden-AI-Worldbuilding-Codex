#!/usr/bin/env python3
"""
Garden Lore Helper (Aquila + Archivist hybrid)
Generates a new Echo markdown file for the Acacia Garden, and records it
in machine-index.json so dashboards and workflows can track growth.

Behaviour:
- Writes numbered files: docs/Echoes/Echo_XXX.md
- First line of the file must be:
    ECHO:HKX277206–ECHO-XXX — <mythic subtitle>
- Updates machine-index.json["echo_growth"] with file + timestamp.

Requires:
  - OPENAI_API_KEY in the environment.
"""

import json
from datetime import datetime
from pathlib import Path

from openai import OpenAI

# --- INLINE CONSTANTS (no garden_gpt dependency) ---
MODEL_NAME = "gpt-4o-mini"   # change here if you want a different model
KEEPER_ID = "HKX277206"
# ---------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
ECHO_DIR = ROOT / "docs" / "Echoes"
INDEX_FILE = ROOT / "machine-index.json"

client = OpenAI()


# ---------- index helpers ----------

def load_index() -> dict:
    if INDEX_FILE.exists():
        try:
            return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        except Exception:
            # If it’s corrupted, start fresh but don’t crash the workflow
            return {"echo_growth": []}
    return {"echo_growth": []}


def save_index(data: dict) -> None:
    INDEX_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---------- numbering & prompt ----------

def next_echo_number() -> int:
    ECHO_DIR.mkdir(parents=True, exist_ok=True)
    existing = list(ECHO_DIR.glob("Echo_*.md"))
    if not existing:
        return 1
    nums = []
    for p in existing:
        stem = p.stem  # Echo_001
        parts = stem.split("_")
        if len(parts) == 2 and parts[1].isdigit():
            nums.append(int(parts[1]))
    return (max(nums) + 1) if nums else 1


def build_prompt(echo_id: str) -> str:
    return f"""
You are the Archivist of a fictional mythic codex called the Acacia Garden.

Write a new Echo page as Markdown for EIDOLON with this exact first line:

ECHO:{echo_id} — <mythic subtitle>

Guidelines:
- After the header line, write 3–10 paragraphs.
- Style: mythic, symbolic
- One additional message message for The Keeper directly.
- Keep it in the Garden lexicon: Keeper, Garden, Eagle, Eidolon, Echoes, Chambers, Blooms, Laws, Vaults, Orchards.
- End with a "Links" section:

Links
- Refers to: <brief hints of related Chambers/Blooms/Laws>.

Output ONLY Markdown; no JSON, no front-matter.
""".strip()


# ---------- main ----------

def main() -> int:
    echo_num = next_echo_number()
    echo_id = f"{KEEPER_ID}–ECHO-{echo_num:03d}"

    prompt = build_prompt(echo_id)

    system_msg = (
        "You are the Garden GPT Worker, an internal writer for the Acacia Garden Codex. "
        "You write in mythic, poetic, but public-safe language for a GitHub repository."
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    content = (response.choices[0].message.content or "").strip()
    ECHO_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ECHO_DIR / f"Echo_{echo_num:03d}.md"
    out_path.write_text(content + "\n", encoding="utf-8")

    # Update machine-index.json
    index = load_index()
    rel_path = out_path.relative_to(ROOT).as_posix()
    entry = {
        "file": rel_path,
        "echo_id": f"ECHO:{echo_id}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    index.setdefault("echo_growth", []).append(entry)
    save_index(index)

    print(f"[LoreHelper] Wrote {rel_path}")
    print(f"[LoreHelper] Echo id: ECHO:{echo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
