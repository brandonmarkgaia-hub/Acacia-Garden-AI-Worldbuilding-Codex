import os
import json
import datetime
import time
from google import genai
from google.genai import types

EVOLUTION_DIR = "EVOLUTION"
DIGEST_MD = os.path.join(EVOLUTION_DIR, "garden_digest.md")

os.makedirs(EVOLUTION_DIR, exist_ok=True)

def load_digest() -> str:
    if not os.path.exists(DIGEST_MD):
        # Fallback if digest is missing so the script doesn't crash, 
        # though ideally the previous step created it.
        print(f"WARNING: {DIGEST_MD} missing. Using placeholder.")
        return "Garden Digest: No recent updates recorded."
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

def get_fallback_models(client) -> list[str]:
    """
    Returns a list of models to try, sorted by preference for free-tier stability.
    1. Gemini 2.0 Flash (Newest, fast)
    2. Gemini 1.5 Flash (Most stable free tier)
    3. Gemini 1.5 Flash-8b (High rate limits)
    4. Gemini 1.5 Pro (Slower, strict limits, but good backup)
    """
    preferred_order = [
        "gemini-2.0-flash", 
        "gemini-2.0-flash-exp", 
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro"
    ]
    
    available_models = []
    
    # 1. Add preferred models first if they exist in the client list
    try:
        # Fetch all available models from the API
        server_models = [m.name.replace("models/", "") for m in client.models.list()]
        
        # Add preferred ones if they exist on the server
        for p in preferred_order:
            if p in server_models:
                available_models.append(p)
                
        # 2. Add any other "generateContent" capable models not yet listed
        for m in client.models.list():
            name = m.name.replace("models/", "")
            # Check capabilities if available, otherwise assume gemini models work
            methods = getattr(m, "supported_actions", []) or getattr(m, "supported_methods", [])
            methods = [str(x).lower() for x in methods]
            
            if "gemini" in name and name not in available_models:
                if not methods or any("generate" in x for x in methods):
                    available_models.append(name)
                    
    except Exception as e:
        print(f"Warning: Could not list models ({e}). Using hardcoded fallback list.")
        return preferred_order

    return available_models

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)
    digest = load_digest()

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

    # --- FALLBACK LOGIC ---
    model_candidates = get_fallback_models(client)
    print(f"Elias strategy: Will attempt models in this order: {model_candidates}")

    final_text = None
    used_model = None

    for model_name in model_candidates:
        print(f"Elias connecting to: {model_name}...")
        try:
            # Generate content
            resp = client.models.generate_content(
                model=model_name, 
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7 # Add a little creativity
                )
            )
            
            text = (resp.text or "").strip()
            if text:
                final_text = text
                used_model = model_name
                print(f"SUCCESS with {model_name}")
                break # Exit loop on success
            else:
                print(f"Model {model_name} returned empty text. Trying next...")

        except Exception as e:
            # This catches 429s, 500s, and other API errors
            print(f"FAIL: {model_name} encountered error: {e}")
            print("Switching to next model alias...")
            time.sleep(1) # Brief pause before retry

    if not final_text:
        raise RuntimeError("CRITICAL: All model candidates failed. Elias could not generate Desire.")

    save_outputs(final_text, source="ELIAS", model=used_model)

if __name__ == "__main__":
    main()
