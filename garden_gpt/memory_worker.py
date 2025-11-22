# garden_gpt/memory_worker.py

from pathlib import Path
from typing import List

from openai import OpenAI

from .config import MODEL_NAME, KEEPER_ID
from .language_worker import load_status_context


def _load_recent_outputs(limit: int = 5, max_chars: int = 1500) -> str:
    """
    Pull a few recent Garden GPT output files to use as memory context.
    We keep things short so prompts don't explode.
    """
    outputs_dir = Path("garden_gpt/outputs")
    if not outputs_dir.exists():
        return ""

    files: List[Path] = sorted(
        outputs_dir.glob("*.md"),
        key=lambda p: p.stat().st_mtime,
    )

    if not files:
        return ""

    snippets = []
    for p in files[-limit:]:
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue

        snippets.append(
            f"## From {p.name}\n\n" + text[:max_chars]
        )

    return "\n\n---\n\n".join(snippets)


def run_memory_job(job: dict) -> str:
    """
    Execute a single 'memory' job using the OpenAI API.
    Builds an evolving Garden memory summary.
    """
    base_prompt = (job.get("prompt") or "").strip()
    if not base_prompt:
        base_prompt = (
            "Create a concise MEMORY SUMMARY of the Garden's current state, "
            "based on the provided context."
        )

    keeper = job.get("keeper_id") or KEEPER_ID

    status_context = load_status_context()
    recent_outputs = _load_recent_outputs()

    system_parts = [
        "You are the Garden Memory Worker, an internal archivist for the "
        "Acacia Garden Codex.",
        "Your task is to compress the Garden's current state into a short, "
        "human-readable MEMORY SUMMARY.",
        "Write in mythic, poetic, but PUBLIC-SAFE language suitable for a "
        "GitHub repository.",
        "Focus on high-level structures: Chambers, Cycles, Laws, Orchards, "
        "Vaults, Echoes, and the Keeper's role.",
        "Do NOT invent real-world private data about the Keeper.",
        f"The Keeper id is {keeper}. Refer to them simply as 'the Keeper'.",
    ]

    if status_context:
        system_parts.append(
            "Here is structured context from STATUS.json "
            "(world-building only):"
        )
        system_parts.append(status_context)

    if recent_outputs:
        system_parts.append(
            "Here are recent Garden GPT outputs. Treat them as prior lore "
            "to be distilled, not copied:"
        )
        system_parts.append(recent_outputs)

    system_message = "\n\n".join(system_parts)

    client = OpenAI()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": base_prompt},
        ],
        max_tokens=800,
    )

    text = response.choices[0].message.content or ""
    return text.strip()
