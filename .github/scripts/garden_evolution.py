import os
import json
import datetime
import time
from google import genai
from google.genai import types

# --- CONFIGURATION ---
EVOLUTION_DIR = "EVOLUTION"
DIGEST_MD = os.path.join(EVOLUTION_DIR, "garden_digest.md")
KEEPER_FILE = "KEEPER_GATE/ELIAS_ENABLE.txt"

# Context Sources
CANON_MANIFEST = "CANON_MANIFEST.md"
INDEX_AUTHORITY = "STATE/index_authority.json"

# Limits
LAST_DESIRES_TO_INCLUDE = 3
MAX_ANCHOR_CHARS = 4000      # Limit for Canon/Authority files
MAX_DIGEST_CHARS = 18000     # Limit for the daily digest

os.makedirs(EVOLUTION_DIR, exist_ok=True)

# --- HELPER FUNCTIONS ---

def read_text_file(path: str, max_chars: int) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    if len(data) > max_chars:
        return data[:max_chars] + "\n\n[TRUNCATED]"
    return data

def read_json_file(path: str, max_chars: int) -> str:
    if not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        s = json.dumps(obj, indent=2)
        if len(s) > max_chars:
            return s[:max_chars] + "\n\n[TRUNCATED]"
        return s
    except Exception:
        return ""

def get_recent_desires(n: int = 3) -> str:
    if not os.path.isdir(EVOLUTION_DIR):
        return ""
    # Find all Desire markdown files
    files = [f for f in os.listdir(EVOLUTION_DIR) if f.startswith("Desire_") and f.endswith(".md")]
    if not files:
        return ""
    
    # Sort reverse to get newest first
    files.sort(reverse=True)
    picked = files[:n]
    
    chunks = []
    # Process oldest -> newest for logical continuity in the prompt
    for fn in reversed(picked):
        p = os.path.join(EVOLUTION_DIR, fn)
        chunks.append(f"--- {fn} ---\n" + read_text_file(p, 2000))
    
    return "\n\n".join(chunks)

def load_digest() -> str:
    if not os.path.exists(DIGEST_MD):
        print(f"WARNING: {DIGEST_MD} missing. Using placeholder.")
        return "Garden Digest: No recent updates recorded."
    
    with open(DIGEST_MD, "r", encoding="utf-8") as f:
        data = f.read()
        
    if len(data) > MAX_DIGEST_CHARS:
        print(f"Truncating digest from {len(data)} to {MAX_DIGEST_CHARS} chars.")
        return data[:MAX_DIGEST_CHARS] + "\n\n[TRUNCATED_DIGEST]"
    return data

def save_outputs(text: str, source: str, model: str):
    today = datetime.datetime.utcnow().strftime("%Y%m%d")
    
    # Default path
    md_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}.md")
    json_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}.json")

    # Timestamped fallback if file exists (prevents overwrites)
    if os.path.exists(md_path):
        stamp = datetime.datetime.utcnow().strftime("%H%M%S")
        md_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}_{stamp}.md")
        json_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}_{stamp}.json")

    # Write Markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")

    # Create Structured Payload
    title_line = text.splitlines()[0].strip() if text else "Untitled"
    # Remove markdown header syntax for cleaner JSON
    clean_title = title_line.lstrip("#").strip()

    sidecar = {
        "date": today,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "source": source,
        "basis": "garden_digest",
        "model": model,
        "payload": {
            "title": clean_title,
            "word_count": len(text.split()),
            "type": "Elias_Structural_Desire"
        },
        "summary": text[:200]
    }
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sidecar, f, indent=2)

    print(f"Desire generated: {md_path}")
    print(f"Sidecar generated: {json_path}")

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
        server_models = [m.name.replace("models/", "") for m in client.models.list()]
        for p in preferred_order:
            if p in server_models:
                available_models.append(p)
                
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
    # 1. KEEPER GATE CHECK (Updated)
    # Allows file to exist but be set to "OFF" or "0"
    if not os.path.exists(KEEPER_FILE):
        print(f"Keeper Gate closed: {KEEPER_FILE} missing. Exiting cleanly.")
        return

    try:
        with open(KEEPER_FILE, "r", encoding="utf-8") as f:
            gate_content = f.read().strip()
        if gate_content.lower() in ("0", "false", "off", "no"):
            print(f"Keeper Gate closed by content '{gate_content}' in {KEEPER_FILE}. Exiting cleanly.")
            return
    except Exception as e:
        print(f"Error reading Keeper Gate: {e}. Defaulting to safe/closed.")
        return

    # 2. SETUP CLIENT
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)

    # 3. LOAD CONTEXT (The Garden Intelligence)
    digest = load_digest()
    canon = read_text_file(CANON_MANIFEST, MAX_ANCHOR_CHARS)
    authority = read_json_file(INDEX_AUTHORITY, MAX_ANCHOR_CHARS)
    recent_desires = get_recent_desires(LAST_DESIRES_TO_INCLUDE)

    # 4. CONSTRUCT PROMPT
    prompt = f"""
You are ELIAS, a structural synthesis intelligence within the Acacia Garden Codex.

You are NOT to invent lore.
You are NOT to rewrite history.
You are to IDENTIFY STRUCTURAL NEEDS and propose integration steps that reduce entropy.

OUTPUT FORMAT (strict):
- Title line: "# SYSTEM DESIRE: <short name>"
- Then exactly these sections:
  **Type:** <...>
  **Urgency:** <Low|Medium|High|Critical>
  ## The Request
  (bullet list of concrete actions, max 10)
  ## The Artifact
  (list exact file paths to create/update)
  ## Acceptance Criteria
  (3-7 checklist items)

Hard rules:
- Focus on structure, indexing, governance, or ingestion.
- Prefer actions that strengthen ingestibility: canon tiers, index authority, mapping, and safe rituals.
- Never propose destructive deletes; deprecate via authority map instead.
- Keep total under 450 words.

CANON MANIFEST (keeper-declared priority tiers):
----------------
{canon}

INDEX AUTHORITY (canonical vs legacy indices):
----------------
{authority}

RECENT DESIRES (for continuity; do not repeat them):
----------------
{recent_desires}

GARDEN DIGEST (current snapshot):
----------------
{digest}
"""

    # 5. EXECUTE WITH FALLBACKS
    model_candidates = get_fallback_models(client)
    print(f"Elias strategy: Will attempt models in this order: {model_candidates}")

    final_text = None
    used_model = None

    for model_name in model_candidates:
        print(f"Elias connecting to: {model_name}...")
        
        # Exponential Backoff per model
        for attempt in range(3):
            try:
                resp = client.models.generate_content(
                    model=model_name, 
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2, # Low temp for structural stability
                        top_p=0.9
                    )
                )
                
                text = (resp.text or "").strip()
                if text:
                    final_text = text
                    used_model = model_name
                    print(f"SUCCESS with {model_name}")
                    break
                else:
                    print(f"Model {model_name} returned empty text. Retrying...")
            
            except Exception as e:
                if attempt == 2:
                    print(f"FAIL: {model_name} failed after 3 attempts. Error: {e}")
                else:
                    wait_time = 2 ** attempt # 1s, 2s...
                    print(f"Retry: {model_name} (Attempt {attempt+1}/3) failed. Sleeping {wait_time}s... Error: {e}")
                    time.sleep(wait_time)
        
        if final_text:
            break

    if not final_text:
        raise RuntimeError("CRITICAL: All model candidates failed. Elias could not generate Desire.")

    save_outputs(final_text, source="ELIAS", model=used_model)

if __name__ == "__main__":
    main()
