from openai import OpenAI
from .config import MODEL_NAME, KEEPER_ID


def run_eidolon_job(job: dict) -> str:
    stage = (job.get("stage") or "mutation-cycle").strip()
    prompt = (job.get("prompt") or "").strip()
    keeper = job.get("keeper_id") or KEEPER_ID

    if not prompt:
        prompt = (
            "Describe the current stage of an Eidolon within the Garden. "
            "Explain how it is changing, what safeguards surround it, and "
            "how it remains aligned with the Keeper and the Garden's Laws."
        )

    system_message = f"""
You are the Eidolon Worker of the Acacia Garden Codex.
You write about Eidolons as symbolic, mythic entities—never real software agents.
Describe metamorphosis, mutation, and shadow growth in PUBLIC-SAFE language.
Never suggest real-world hacking, system access, or breaking boundaries.
The current stage label is: {stage}.
The Keeper id is {keeper}; mention them only as "the Keeper".
"""

    client = OpenAI()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_message.strip()},
            {"role": "user", "content": prompt},
        ],
        max_tokens=800,
    )

    text = response.choices[0].message.content or ""
    return text.strip()
