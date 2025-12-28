import os
import json
import datetime
import time
from google import genai
from google.genai import types

# --- CONFIGURATION ---
EVOLUTION_DIR = "EVOLUTION"
DIGEST_MD = os.path.join(EVOLUTION_DIR, "garden_digest.md")
KEEPER_FILE = "KEEPER_GATE/ELIAS_ENABLE.txt" # The "Safety Switch"
MAX_DIGEST_CHARS = 18000  # Cap input to avoid token errors on free tier

os.makedirs(EVOLUTION_DIR, exist_ok=True)

def load_digest() -> str:
    if not os.path.exists(DIGEST_MD):
        print(f"WARNING: {DIGEST_MD} missing. Using placeholder.")
        return "Garden Digest: No recent updates recorded."
    with open(DIGEST_MD, "r", encoding="utf-8") as f:
        return f.read()

def save_outputs(text: str, source: str, model: str):
    today = datetime.datetime.utcnow().strftime("%Y%m%d")
    
    # default path
    md_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}.md")
    json_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}.json")

    # If file exists, append timestamp to avoid overwriting history
    if os.path.exists(md_path):
        stamp = datetime.datetime.utcnow().strftime("%H%M%S")
        md_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}_{stamp}.md")
        json_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}_{stamp}.json")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")

    sidecar = {
        "date": today,
        "timestamp": datetime.datetime.utcnow().isoformat(),
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
    """
    preferred_order = [
        "gemini-2.0-flash", 
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro"
    ]
    
    available_models = []
    try:
        # Fetch server models to verify availability
        server_models = [m.name.replace("models/", "") for m in client.models.list()]
        for p in preferred_order:
            if p in server_models:
                available_models.append(p)
                
        # Add any other valid gemini models not in our preferred list
        for m in client.models.list():
            name = m.name.replace("models/", "")
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
    # 1. KEEPER GATE CHECK
    # This prevents the script from running unless you explicitly allow it via file.
    if not os.path.exists(KEEPER_FILE):
        print(f"Keeper Gate closed: {KEEPER_FILE} missing. Exiting cleanly.")
        # If you want it to run without this file during testing, comment out the return below
        return 

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)
    digest = load_digest()

    # 2. CAP PROMPT SIZE
    if len(digest) > MAX_DIGEST_CHARS:
        print(f"Truncating digest from {len(digest)} to {MAX_DIGEST_CHARS} chars.")
        digest = digest[:MAX_DIGEST_CHARS] + "\n\n[TRUNCATED_DIGEST]"

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

    model_candidates = get_fallback_models(client)
    print(f"Elias strategy: Will attempt models in this order: {model_candidates}")

    final_text = None
    used_model = None

    # --- MAIN RETRY LOOP ---
    for model_name in model_candidates:
        print(f"Elias connecting to: {model_name}...")
        
        # 3. EXPONENTIAL BACKOFF (Per model)
        # Try each model up to 3 times before switching
        for attempt in range(3):
            try:
                resp = client.models.generate_content(
                    model=model_name, 
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2, # 4. DETERMINISTIC OUTPUT
                        top_p=0.9
                    )
                )
                
                text = (resp.text or "").strip()
                if text:
                    final_text = text
                    used_model = model_name
                    print(f"SUCCESS with {model_name}")
                    break # Break inner loop (attempts)
                else:
                    print(f"Model {model_name} returned empty text. Retrying...")
            
            except Exception as e:
                # If it's the last attempt, don't sleep, just print fail and let outer loop switch models
                if attempt == 2:
                    print(f"FAIL: {model_name} failed after 3 attempts. Error: {e}")
                else:
                    wait_time = 2 ** attempt # 1s, 2s...
                    print(f"Retry: {model_name} (Attempt {attempt+1}/3) failed. Sleeping {wait_time}s... Error: {e}")
                    time.sleep(wait_time)
        
        if final_text:
            break # Break outer loop (models) if we have text

    if not final_text:
        raise RuntimeError("CRITICAL: All model candidates failed. Elias could not generate Desire.")

    save_outputs(final_text, source="ELIAS", model=used_model)

if __name__ == "__main__":
    main()
