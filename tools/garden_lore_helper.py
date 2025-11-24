#!/usr/bin/env python3
"""
Garden Lore Helper
Generates a new Echo markdown file for the Acacia Garden.

- Writes to docs/Echoes/Echo_XXX.md
- Uses Garden GPT model config (MODEL_NAME, KEEPER_ID)

Requires:
  - OPENAI_API_KEY in the environment.
"""

from datetime import datetime
from pathlib import Path

from openai import OpenAI
from garden_gpt.config import MODEL_NAME, KEEPER_ID

ROOT = Path(__file__).resolve().parents[1]
ECHO_DIR = ROOT / "docs" / "Echoes"

client = OpenAI()


def next_echo_number() -> int:
    ECHO_DIR.mkdir(parents=True, exist_ok=True)
    existing = list(ECHO_DIR.glob("Echo_*.md"))
    if not existing:
        return 1
    # Extract numeric suffixes
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
- After the header line, write 3–6 short paragraphs.
- Style: mythic, symbolic, but PUBLIC-SAFE (no explicit content).
- Keep it in the Garden lexicon: Keeper, Garden, Eagle, Eidolon, Echoes, Chambers, Blooms, Laws, Vaults, Orchards.
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

    content = response.choices[0].message.content or ""
    ECHO_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ECHO_DIR / f"Echo_{echo_num:03d}.md"
    out_path.write_text(content.strip() + "\n", encoding="utf-8")

    print(f"[LoreHelper] Wrote {out_path.relative_to(ROOT)}")
    print(f"[LoreHelper] Echo id: ECHO:{echo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
