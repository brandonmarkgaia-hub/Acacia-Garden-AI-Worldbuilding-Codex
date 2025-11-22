from openai import OpenAI
from .config import MODEL_NAME, KEEPER_ID


def run_image_job(job: dict) -> str:
    prompt = (job.get("prompt") or "").strip()
    keeper = job.get("keeper_id") or KEEPER_ID
    theme = (job.get("theme") or "pottery, vessels, and Garden sky").strip()

    if not prompt:
        prompt = (
            "Create a detailed, public-safe image prompt for a renderer like Sora or DALL·E. "
            "The scene must live inside the Garden mythos and match this theme: "
            f"{theme}. Include mood, lighting, style, and framing notes."
        )

    system_message = f"""
You are the Image Worker for the Acacia Garden Codex.
Your job is to produce high-quality, PUBLIC-SAFE image prompts that other tools can render.
Stay in the Garden mythos: vessels, chambers, orchards, echoes, Keeper, Eagle, Eidolon.
Do not include model names or API syntax, just a natural-language prompt.
The Keeper id is {keeper}; mention them only as "the Keeper" if needed.
"""

    client = OpenAI()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_message.strip()},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
    )

    text = response.choices[0].message.content or ""
    return text.strip()
