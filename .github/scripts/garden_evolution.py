import os
import json
import datetime

from google import genai

EVOLUTION_DIR = "EVOLUTION"
DIGEST_MD = os.path.join(EVOLUTION_DIR, "garden_digest.md")

os.makedirs(EVOLUTION_DIR, exist_ok=True)

def load_digest() -> str:
    if not os.path.exists(DIGEST_MD):
        raise RuntimeError("EVOLUTION/garden_digest.md missing – digest must run first")
    with open(DIGEST_MD, "r", encoding="utf-8") as f:
        return f.read()

def save_outputs(text: str, source: str, model: str):
    today = datetime.datetime.utcnow().strftime("%Y%m%d")
    md_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}.md")
    json_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}.json")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")

    sidecar = {
        "date": today,
        "source": source,
        "basis": "garden_digest",
        "model": model,
        "summary": text.splitlines()[0][:180] if text else ""
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sidecar, f, indent=2)

    print(f"Desire generated: {md_path} (source={source}, model={model})")

def pick_model(client) -> str:
    """
    Pick the first model that supports generateContent and isn't obviously restricted.
    This avoids hardcoding a model your project can't use.
    """
    # NOTE: model objects vary a bit by SDK version; we defensively read attrs.
    candidates = []
    for m in client.models.list():
        name = getattr(m, "name", "") or ""
        methods = getattr(m, "supported_actions", None) or getattr(m, "supported_methods", None) or []
        # normalize to strings
        methods = [str(x) for x in methods]

        # Heuristic: only keep Gemini models likely to support text generation
        if "gemini" in name.lower():
            # Some SDKs don't expose supported methods well; keep as candidate anyway.
            candidates.append((name, methods))

    # Prefer flash models first
    candidates.sort(key=lambda x: ("flash" not in x[0].lower(), x[0]))

    if not candidates:
        raise RuntimeError("No gemini models found via client.models.list()")

    # If methods are exposed, filter for generateContent; otherwise try in order
    for name, methods in candidates:
        if not methods or any("generate" in m.lower() for m in methods):
            return name

    return candidates[0][0]

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)
    digest = load_digest()

    model_name = pick_model(client)
    print(f"Using model: {model_name}")

    prompt = f"""
You are ELIAS, a structural synthesis intelligence within the Acacia Garden Codex.

You are NOT to invent lore.
You are NOT to rewrite history.
You are to IDENTIFY STRUCTURAL NEEDS.

Using the Garden Digest below, generate ONE SYSTEM DESIRE.

Rules:
- Focus on structure, indexing, governance, or ingestion
- No mythic prose beyond naming
- Output MUST be valid Markdown
- Include: Type, Urgency, Request
- Keep under 400 words

Garden Digest:
----------------
{digest}
"""

    resp = client.models.generate_content(model=model_name, contents=prompt)
    text = (resp.text or "").strip()
    if not text:
        raise RuntimeError("Model returned empty response.text")

    save_outputs(text, source="ELIAS", model=model_name)

if __name__ == "__main__":
    main()
