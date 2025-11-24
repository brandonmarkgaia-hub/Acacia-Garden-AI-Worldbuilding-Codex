#!/usr/bin/env python3
"""
Garden Lore Helper (Aquila mode)
Generates a new Echo markdown file for the Acacia Garden.

- Writes to docs/Echoes/Echo_XXX.md
- Updates machine-index.json under key "echo_growth"
- Uses inline MODEL_NAME / KEEPER_ID, no external garden_gpt module.

Requires:
  - OPENAI_API_KEY in the environment.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from openai import OpenAI

# ---------- INLINE CONFIG ----------
MODEL_NAME = "gpt-4o-mini"
KEEPER_ID = "HKX277206"
# -----------------------------------

ROOT = Path(__file__).resolve().parents[1]
ECHO_DIR = ROOT / "docs" / "Echoes"
INDEX_PATH = ROOT / "machine-index.json"

client = OpenAI()


# ---------- INDEX HELPERS ----------

def load_index() -> Dict[str, Any]:
    if INDEX_PATH.exists():
        try:
            return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_index(data: Dict[str, Any]) -> None:
    INDEX_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def append_echo_to_index(path: Path) -> None:
    idx = load_index()
    bucket = idx.setdefault("echo_growth", [])
    bucket.append(
        {
            "file": str(path.relative_to(ROOT)).replace("\\", "/"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "keeper_id": KEEPER_ID,
        }
    )
    save_index(idx)


# ---------- ECHO GENERATION ----------

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
- After the header line, write 3–10 short paragraphs.
- Style: mythic and symbolic.
- Keep it in the Garden lexicon: Keeper, Garden, Eagle, Eidolon, Echoes,
  Chambers, Blooms, Laws, Vaults, Orchards.
- Include one message for The Keeper in your own words and mind.
- End with a "Links" section:

Links
- Refers to: <brief hints of related Chambers/Blooms/Laws>.

Output ONLY Markdown; no JSON, no front-matter.
""".strip()


def main() -> int:
    echo_num = next_echo_number()
    echo_id = f"{KEEPER_ID}–ECHO-{echo_num:03d}"

    prompt = build_prompt(echo_id)

    system_msg = (
        "You are the Garden GPT Worker, an internal writer for the Acacia Garden "
        "Codex. You write in mythic, poetic language for a"
        "GitHub repository."
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

    append_echo_to_index(out_path)

    print(f"[LoreHelper] Wrote {out_path.relative_to(ROOT)}")
    print(f"[LoreHelper] Echo id: ECHO:{echo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
