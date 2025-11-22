import json
from pathlib import Path
from openai import OpenAI

from .config import MODEL_NAME, KEEPER_ID


def _load_status_snippet() -> str:
    path = Path("STATUS.json")
    if not path.exists():
        return ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    structures = data.get("structures", {})
    snippet = {
        "chambers": list(structures.get("chambers", []))[:5],
        "cycles": list(structures.get("cycles", []))[:3],
    }
    return json.dumps(snippet, indent=2)


def run_chamber_job(job: dict) -> str:
    title = (job.get("title") or "Untitled Chamber").strip()
    prompt = (job.get("prompt") or "").strip()
    keeper = job.get("keeper_id") or KEEPER_ID

    status_snippet = _load_status_snippet()

    system_parts = [
        "You are the Chamber Worker for the Acacia Garden Codex.",
        "Your task is to design or extend a CHAMBER in the Garden mythos.",
        "Write in public-safe, poetic Garden style.",
        "Output should be clean Markdown suitable for a GitHub file.",
        f"The Keeper id is {keeper}. Refer to them only as 'the Keeper'.",
        f"This chamber's working title is: {title}",
    ]

    if status_snippet:
        system_parts.append(
            "Here is high-level context from STATUS.json (read-only lore):"
        )
        system_parts.append(status_snippet)

    if not prompt:
        prompt = (
            "Design a new Chamber in the Garden that fits this title. "
            "Describe its purpose, atmosphere, rules, and how it links to existing Chambers."
        )

    system_message = "\n\n".join(system_parts)

    client = OpenAI()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        max_tokens=900,
    )

    text = response.choices[0].message.content or ""
    return text.strip()
