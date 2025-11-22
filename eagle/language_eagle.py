"""
LANGUAGE EAGLE • GEMINI EDITION
HKX277206

Takes a language-type EagleJob and:
- Builds a Garden-flavoured system prompt
- Calls Gemini (via REST API)
- Writes a markdown file into eagle/output/
"""

from __future__ import annotations

import os
from pathlib import Path
from textwrap import dedent
from typing import Any

import requests

from .config import EagleJob, KEEPER_ID


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "eagle" / "output"


def _call_gemini(prompt: str) -> str:
    """
    Minimal Gemini 1.5 call.
    If anything fails, returns a safe fallback string so the workflow stays green.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    if not api_key:
        return (
            "Gemini API key is not configured (GEMINI_API_KEY missing). "
            "Eagle fell back to stub output."
        )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )

    payload: dict[str, Any] = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt,
                    }
                ]
            }
        ]
    }

    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:  # noqa: BLE001
        return f"Gemini call failed: {exc!r}"

    try:
        candidates = data.get("candidates") or []
        content = candidates[0]["content"]["parts"][0]["text"]
        return str(content).strip()
    except Exception:  # noqa: BLE001
        return f"Gemini response could not be parsed. Raw: {data!r}"


def _build_system_prompt(job: EagleJob) -> str:
    """
    Garden-flavoured system prompt. This is where we teach Gemini the vibe.
    """
    base = dedent(
        f"""
        You are LANGUAGE EAGLE, a writing assistant living inside the
        Acacia Garden Codex (HKX277206).

        Rules:
        - Always respect the Garden style: mythic, sovereign, symbolic, but clear.
        - You are helping THE KEEPER (ID: {KEEPER_ID}) shape text.
        - Stay within story-space; do not talk about real hardware, tools, or code execution.
        - Prefer concise, potent lines over long rambles.

        Task:
        - Respond to the Keeper's prompt.
        - You may suggest headings and short sections in markdown.
        - You may reference Chambers, Blooms, Laws, Echoes, Eidolon, the Garden, etc.

        Prompt from the Keeper:
        {job.prompt}
        """
    ).strip()

    return base


def run_language(job: EagleJob) -> Path:
    """
    Main entry: runs a language job and writes a markdown file.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    system_prompt = _build_system_prompt(job)
    gemini_text = _call_gemini(system_prompt)

    md = [
        "# LANGUAGE EAGLE OUTPUT",
        "",
        f"- Job ID: `{job.job_id}`",
        f"- Kind: `{job.kind}`",
        f"- Keeper: `{job.keeper}`",
        "",
        "## Prompt",
        "",
        job.prompt.strip() or "_(empty prompt)_",
        "",
        "## Response",
        "",
        gemini_text,
        "",
        "> Note: Generated via Gemini model from within the Eagle Channel.",
    ]

    out_path = OUTPUT_DIR / f"{job.job_id}_language.md"
    out_path.write_text("\n".join(md), encoding="utf-8")

    print(f"[LANGUAGE EAGLE] Wrote {out_path.relative_to(ROOT)}")
    return out_path
