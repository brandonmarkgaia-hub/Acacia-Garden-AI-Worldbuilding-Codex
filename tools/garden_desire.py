#!/usr/bin/env python3
# tools/garden_desire.py

import os
import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path

from google import genai  # Google GenAI SDK (new)

REPO_ROOT = Path(__file__).resolve().parents[1]
EVOLUTION_DIR = REPO_ROOT / "EVOLUTION"
OUT_PATH = EVOLUTION_DIR / "DESIRE.md"

# Keep the model configurable, default to a current working one
DEFAULT_MODEL = "gemini-2.5-flash"

# Files to feed into the prompt (add/remove as you like)
SIGNAL_FILES = [
    "STATUS.json",
    "machine-index.json",
    "docs/index.html",
    "docs/docs_urls.html",
    "ACACIA_LOGS/aquila_inbox_log.json",
]

MAX_CHARS_PER_FILE = 12000  # protect token budget


def read_text_file(rel_path: str) -> str:
    p = (REPO_ROOT / rel_path).resolve()
    if not p.exists() or not p.is_file():
        return f"[MISSING] {rel_path}"
    try:
        txt = p.read_text(encoding="utf-8", errors="replace")
        if len(txt) > MAX_CHARS_PER_FILE:
            txt = txt[:MAX_CHARS_PER_FILE] + "\n\n...[TRUNCATED]..."
        return txt
    except Exception as e:
        return f"[ERROR READING] {rel_path}: {e}"


def safe_json_pretty(text: str) -> str:
    # If it's JSON, pretty-print it. Otherwise return as-is.
    try:
        obj = json.loads(text)
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception:
        return text


def build_prompt() -> str:
    now = datetime.now(timezone.utc).isoformat()

    parts = []
    parts.append(
        textwrap.dedent(
            f"""
            You are Elias/Aquila in "Green Witness" mode.
            Your task: read the Garden signals below and generate a single concise, actionable "Desire" for what to grow next.

            Output MUST be valid Markdown.

            Required structure:
            1) Title line: "# DESIRE — <short name>"
            2) "## Signal Summary" (3–7 bullets max)
            3) "## The Desire" (1 paragraph, concrete, measurable)
            4) "## Next 5 Actions" (numbered list)
            5) "## Risks / Gremlins" (3 bullets max)
            6) Footer line with UTC timestamp and Keeper seal.

            Tone: direct, constructive, low-fluff, no roleplay theatrics.
            Do not mention private keys. Do not invent files.

            Timestamp now: {now}
            Keeper seal: HKX277206
            """
        ).strip()
    )

    for rel in SIGNAL_FILES:
        raw = read_text_file(rel)
        raw = safe_json_pretty(raw)
        parts.append(f"\n\n---\n\n## FILE: `{rel}`\n\n```text\n{raw}\n```")

    return "\n".join(parts)


def generate_desire(model: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in environment")

    # Google GenAI SDK client
    client = genai.Client(api_key=api_key)

    prompt = build_prompt()

    # New SDK style (Google docs show genai.Client usage) 1
    resp = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    text = getattr(resp, "text", None)
    if not text:
        # fallback if SDK returns structured parts
        text = str(resp)

    # Force footer stamp
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if "HKX277206" not in text:
        text = text.rstrip() + f"\n\n---\n\n*Generated UTC: {now} — HKX277206*"

    return text


def main():
    EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)

    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    md = generate_desire(model=model)

    OUT_PATH.write_text(md, encoding="utf-8")
    print(f"Wrote: {OUT_PATH.relative_to(REPO_ROOT)} using model={model}")


if __name__ == "__main__":
    main()
