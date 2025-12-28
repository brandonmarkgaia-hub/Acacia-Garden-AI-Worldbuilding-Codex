import os
import json
import datetime
import time
import re
from google import genai
from google.genai import types

# --- CONFIGURATION ---
EVOLUTION_DIR = "EVOLUTION"
DIGEST_MD = os.path.join(EVOLUTION_DIR, "garden_digest.md")
KEEPER_FILE = "KEEPER_GATE/ELIAS_ENABLE.txt"  # Safety Switch

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
    files = [f for f in os.listdir(EVOLUTION_DIR) if f.startswith("Desire_") and f.endswith(".md")]
    if not files:
        return ""
    files.sort(reverse=True)
    picked = files[:n]

    chunks = []
    for fn in reversed(picked):  # oldest -> newest for continuity
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

def keeper_gate_open() -> bool:
    if not os.path.exists(KEEPER_FILE):
        print(f"Keeper Gate closed: {KEEPER_FILE} missing. Exiting cleanly.")
        return False

    try:
        with open(KEEPER_FILE, "r", encoding="utf-8") as f:
            gate_content = f.read().strip()
        if gate_content.lower() in ("0", "false", "off", "no"):
            print(f"Keeper Gate closed by content '{gate_content}' in {KEEPER_FILE}. Exiting cleanly.")
            return False
    except Exception as e:
        print(f"Error reading Keeper Gate: {e}. Defaulting to safe/closed.")
        return False

    return True

def sanitize_elias_markdown(text: str) -> str:
    """
    Fixes a common failure mode where the model wraps output in ```markdown fences.
    Also strips leading BOMs and excess whitespace.
    """
    if not text:
        return text

    t = text.replace("\ufeff", "").strip()
    lines = t.splitlines()

    # If the first non-empty line is a fence, remove it
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].strip().startswith("```"):
        # drop first fence line
        lines = lines[:i] + lines[i+1:]

        # drop trailing fence if present
        j = len(lines) - 1
        while j >= 0 and not lines[j].strip():
            j -= 1
        if j >= 0 and lines[j].strip() == "```":
            lines = lines[:j]

    # If STILL starts with a fence (some models double-wrap), strip again
    while lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    while lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip()

def extract_clean_title(text: str) -> str:
    """
    Title used for sidecar payload. Prefer first markdown heading after sanitization.
    """
    if not text:
        return "Untitled"
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            return s.lstrip("#").strip()[:180]
        return s[:180]
    return "Untitled"

def save_outputs(text: str, source: str, model: str):
    today = datetime.datetime.utcnow().strftime("%Y%m%d")

    md_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}.md")
    json_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}.json")

    # Timestamped fallback if file exists (prevents overwrites)
    if os.path.exists(md_path):
        stamp = datetime.datetime.utcnow().strftime("%H%M%S")
        md_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}_{stamp}.md")
        json_path = os.path.join(EVOLUTION_DIR, f"Desire_{today}_{stamp}.json")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")

    clean_title = extract_clean_title(text)

    # Better summary: first 3 non-empty lines, joined
    summary_lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    summary = " ".join(summary_lines[:3])[:240]

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
        "summary": summary
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sidecar, f, indent=2)

    print(f"Desire generated: {md_path}")
    print(f"Sidecar generated: {json_path}")

def get_fallback_models(client) -> list[str]:
    """
    Returns a list of models to try, sorted by preference.
    Single list() call to reduce quota + time.
    """
    preferred_order = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro"
    ]

    try:
        models = list(client.models.list())
        server_models = [m.name.replace("models/", "") for m in models]

        available_models = [p for p in preferred_order if p in server_models]

        for m in models:
            name = m.name.replace("models/", "")
            methods = getattr(m, "supported_actions", []) or getattr(m, "supported_methods", [])
            methods = [str(x).lower() for x in methods]

            if "gemini" in name and name not in available_models:
                if not methods or any("generate" in x for x in methods):
                    available_models.append(name)

        return available_models or preferred_order

    except Exception as e:
        print(f"Warning: Could not list models ({e}). Using hardcoded fallback list.")
        return preferred_order

def build_prompt(digest: str, canon: str, authority: str, recent_desires: str) -> str:
    return f"""
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
- Do NOT wrap your output in triple-backtick code fences.
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

def is_quota_or_rate_error(e: Exception) -> bool:
    msg = str(e).lower()
    return (
        "resource_exhausted" in msg
        or "quota" in msg
        or "rate limit" in msg
        or "429" in msg
    )

def generate_desire(client, prompt: str) -> tuple[str, str] | tuple[None, None]:
    model_candidates = get_fallback_models(client)
    print(f"Elias strategy: Will attempt models in this order: {model_candidates}")

    for model_name in model_candidates:
        print(f"Elias connecting to: {model_name}...")

        for attempt in range(3):
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        top_p=0.9
                    )
                )
                text = (resp.text or "").strip()
                if text:
                    print(f"SUCCESS with {model_name}")
                    return text, model_name
                else:
                    print(f"Model {model_name} returned empty text. Retrying...")

            except Exception as e:
                if is_quota_or_rate_error(e):
                    print(f"Quota/rate limited detected ({e}). Exiting cleanly without failing the workflow.")
                    return None, None

                if attempt == 2:
                    print(f"FAIL: {model_name} failed after 3 attempts. Error: {e}")
                else:
                    wait_time = 2 ** attempt  # 1s, 2s...
                    print(f"Retry: {model_name} (Attempt {attempt+1}/3) failed. Sleeping {wait_time}s... Error: {e}")
                    time.sleep(wait_time)

    return None, None

def main():
    if not keeper_gate_open():
        return

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)

    digest = load_digest()

    canon = read_text_file(CANON_MANIFEST, MAX_ANCHOR_CHARS) or "[MISSING_CANON_MANIFEST]"
    authority = read_json_file(INDEX_AUTHORITY, MAX_ANCHOR_CHARS) or "{ }  # [MISSING_INDEX_AUTHORITY]"
    recent_desires = get_recent_desires(LAST_DESIRES_TO_INCLUDE) or "[NO_RECENT_DESIRES]"

    prompt = build_prompt(digest, canon, authority, recent_desires)

    text, used_model = generate_desire(client, prompt)
    if not text:
        print("No Desire generated in this run.")
        return

    # 🔥 Critical fix: prevent ```markdown wrappers from polluting downstream tools
    text = sanitize_elias_markdown(text)

    save_outputs(text, source="ELIAS", model=used_model)

if __name__ == "__main__":
    main()
