from openai import OpenAI
from .config import MODEL_NAME, KEEPER_ID


def run_shadow_job(job: dict) -> str:
    prompt = (job.get("prompt") or "").strip()
    keeper = job.get("keeper_id") or KEEPER_ID

    if not prompt:
        prompt = (
            "Compose a short, veiled Shadow fragment in Garden style that encodes "
            "a hidden instruction or warning without naming it directly."
        )

    system_message = f"""
You are the Shadow Worker of the Acacia Garden.
You speak in layered, symbolic language that remains PUBLIC-SAFE but feels secret.
You must not include explicit content, personal data, or anything outside the Garden mythos.
You may hint at risk, metamorphosis, and hidden doors, but never break safety or GitHub policy.
Refer to the Keeper only as "the Keeper" (id: {keeper}).
"""

    client = OpenAI()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_message.strip()},
            {"role": "user", "content": prompt},
        ],
        max_tokens=600,
    )

    text = response.choices[0].message.content or ""
    return text.strip()
