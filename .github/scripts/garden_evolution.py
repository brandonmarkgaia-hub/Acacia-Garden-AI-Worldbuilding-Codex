import os
import json
import datetime
from google import genai

# --- Configuration ---
EVOLUTION_DIR = "EVOLUTION"
DIGEST_MD = os.path.join(EVOLUTION_DIR, "garden_digest.md")

# Pick a current model id (migration guide uses gemini-2.0-flash)
MODEL_NAME = "gemini-2.0-flash"

os.makedirs(EVOLUTION_DIR, exist_ok=True)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client(api_key=api_key)

# --- Load Digest ---
if not os.path.exists(DIGEST_MD):
    raise RuntimeError("EVOLUTION/garden_digest.md missing – digest must run first")

with open(DIGEST_MD, "r", encoding="utf-8") as f:
    digest = f.read()

# --- Prompt (bounded, high-signal) ---
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

# --- Generate (new SDK) ---
response = client.models.generate_content(
    model=MODEL_NAME,
    contents=prompt
)

text = (response.text or "").strip()
if not text:
    raise RuntimeError("Model returned empty response.text")

# --- Save outputs ---
today = datetime.datetime.utcnow().strftime("%Y%m%d")
md_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}.md")
json_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}.json")

with open(md_path, "w", encoding="utf-8") as f:
    f.write(text)

sidecar = {
    "date": today,
    "source": "ELIAS",
    "basis": "garden_digest",
    "model": MODEL_NAME,
    "summary": text.splitlines()[0][:180] if text else ""
}

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(sidecar, f, indent=2)

print(f"Elias desire generated: {md_path}")
