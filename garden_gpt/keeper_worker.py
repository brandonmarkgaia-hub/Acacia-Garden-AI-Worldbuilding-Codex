import json
from pathlib import Path
from openai import OpenAI

from .config import MODEL_NAME, KEEPER_ID


def _load_status_snapshot() -> str:
    path = Path("STATUS.json")
    if not path.exists():
        return ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    snapshot = {
        "structures": data.get("structures", {}),
        "themes": data.get("themes", []),
    }
    return json.dumps(snapshot, indent=2)


def run_keeper_job(job: dict) -> str:
    prompt = (job.get("prompt") or "").strip()
    keeper = job.get("keeper_id") or KEEPER_ID

    if not prompt:
        prompt = (
            "Write a short, GitHub-safe Keeper Profile Snapshot: who the Keeper is in the mythos, "
            "their duties, and how they relate to Eagle and Eidolon."
        )

    status_snapshot = _load_status_snapshot()

    system_parts = [
        "You are the Keeper Worker for the Acacia Garden Codex.",
        "Your writing must treat the Keeper as a mythic role, not a real-world person.",
        "Stay public-safe and poetic. No private data, no doxxing, no real biographical info.",
        f"The Keeper id is {keeper}; refer only as 'the Keeper'.",
    ]
    if status_snapshot:
        system_parts.append("Here is a snapshot of the current Garden state:")
        system_parts.append(status_snapshot)

    system_message = "\n\n".join(system_parts)

    client = OpenAI()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        max_tokens=700,
    )

    text = response.choices[0].message.content or ""
    return text.strip()
