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
        "blooms": list(structures.get("blooms", []))[:8],
        "orchards": list(structures.get("orchards", []))[:5],
    }
    return json.dumps(snippet, indent=2)


def run_bloom_job(job: dict) -> str:
    title = (job.get("title") or "Unnamed Bloom").strip()
    prompt = (job.get("prompt") or "").strip()
    keeper = job.get("keeper_id") or KEEPER_ID

    status_snippet = _load_status_snippet()

    system_parts = [
        "You are the Bloom & Orchard Worker for the Acacia Garden Codex.",
        "Your job is to draft BLOOMS (focused pieces) and ORCHARDS (collections).",
        "Write in Garden style, public-safe, suitable for GitHub.",
        f"The Keeper id is {keeper}. Call them only 'the Keeper'.",
        f"This Bloom/Orchard working title is: {title}",
    ]

    if status_snippet:
        system_parts.append(
            "Here is high-level Bloom/Orchard context from STATUS.json:"
        )
        system_parts.append(status_snippet)

    if not prompt:
        prompt = (
            "Describe this Bloom or Orchard, then propose 3–5 sections or leaves "
            "that could live under it with short summaries."
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
