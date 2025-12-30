import os
import json
import datetime
import time
import re
from pathlib import Path

import yaml
from google import genai
from google.genai import types


# -----------------------------
# Constants / Paths
# -----------------------------
EVOLUTION_DIR = "EVOLUTION"
DIGEST_MD = os.path.join(EVOLUTION_DIR, "garden_digest.md")
DIGEST_JSON = os.path.join(EVOLUTION_DIR, "garden_digest.json")

DESIRE_DIR = os.path.join(EVOLUTION_DIR, "desires")
DESIRE_MD = os.path.join(DESIRE_DIR, "Elias_Desire.md")
DESIRE_JSON = os.path.join(DESIRE_DIR, "Elias_Desire.json")

CANON_MANIFEST = "CANON_MANIFEST.md"
INDEX_AUTHORITY = "STATE/index_authority.json"

KEEPER_SEAL = "HKX277206"

# Limits
MAX_ANCHOR_CHARS = 16000
LAST_DESIRES_TO_INCLUDE = 2


# -----------------------------
# Utilities
# -----------------------------
def now_utc_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def read_text_file(path: str, max_chars: int) -> str | None:
    try:
        p = Path(path)
        if not p.exists():
            return None
        txt = p.read_text(encoding="utf-8", errors="ignore")
        return txt[:max_chars]
    except Exception:
        return None


def read_json_file(path: str, max_chars: int) -> str | None:
    try:
        p = Path(path)
        if not p.exists():
            return None
        txt = p.read_text(encoding="utf-8", errors="ignore")
        return txt[:max_chars]
    except Exception:
        return None


def keeper_gate_open() -> bool:
    """
    Simple guard: if you ever want to hard-stop runs unless Keeper seal is present in env,
    this is where you do it. Right now it just returns True.
    """
    return True


def is_quota_or_rate_error(e: Exception) -> bool:
    s = str(e).lower()
    return any(
        k in s
        for k in [
            "429",
            "resource_exhausted",
            "rate limit",
            "ratelimit",
            "quota",
            "too many requests",
            "exceeded your current quota",
            "retryinfo",
        ]
    )


def sanitize_elias_markdown(text: str) -> str:
    """
    Prevent ```markdown wrappers / fenced code blocks from polluting downstream tools.
    """
    if not text:
        return text

    # Strip leading/trailing fence wrappers if model wraps entire response.
    text = text.strip()

    # Remove outer ```markdown ... ``` or ``` ... ```
    outer = re.match(r"^```(?:markdown)?\s*([\s\S]*?)\s*```$", text, flags=re.IGNORECASE)
    if outer:
        text = outer.group(1).strip()

    return text


def get_recent_desires(n: int) -> str | None:
    """
    Pull the last N desire markdowns if they exist.
    """
    d = Path(DESIRE_DIR)
    if not d.exists():
        return None

    # If you keep multiple desires, you can adapt naming + sorting here.
    # For now, just include the current Desire file if it exists.
    p = Path(DESIRE_MD)
    if p.exists():
        return p.read_text(encoding="utf-8", errors="ignore")[:MAX_ANCHOR_CHARS]

    return None


def load_digest() -> dict:
    """
    Load digest json if present; otherwise load markdown if present.
    """
    p_json = Path(DIGEST_JSON)
    if p_json.exists():
        try:
            return json.loads(p_json.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            pass

    p_md = Path(DIGEST_MD)
    if p_md.exists():
        return {"digest_md": p_md.read_text(encoding="utf-8", errors="ignore")[:MAX_ANCHOR_CHARS]}

    return {"digest_md": "[MISSING_DIGEST]"}


# -----------------------------
# Model Selection (Echoes-style fallback)
# -----------------------------
def get_fallback_models(client) -> list[str]:
    """
    IMPORTANT: Start Pro/Preview first (paid/preview quota pool),
    then fall back to Flash. Also includes dynamic discovery.
    """
    preferred_order = [
        "gemini-2.5-pro",
        "gemini-2.5-pro-preview",
        "gemini-3-flash-preview",
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
    ]

    try:
        models = list(client.models.list())
        server_models = [m.name.replace("models/", "") for m in models]

        available_models = [p for p in preferred_order if p in server_models]

        # Add other gemini models discovered on server (stable-ish ordering)
        for m in models:
            name = m.name.replace("models/", "")
            methods = getattr(m, "supported_actions", []) or getattr(m, "supported_methods", [])
            methods = [str(x).lower() for x in methods]

            if "gemini" in name and name not in available_models:
                # Keep ones that can generate content
                if not methods or any("generate" in x for x in methods):
                    available_models.append(name)

        # If nothing matched, fallback to something sane
        return available_models or ["gemini-3-flash-preview", "gemini-2.0-flash"]
    except Exception:
        return ["gemini-3-flash-preview", "gemini-2.0-flash"]


# -----------------------------
# Prompt Builder
# -----------------------------
def build_prompt(digest: dict, canon: str, authority: str, recent_desires: str) -> str:
    """
    Build the Desire prompt.
    """
    digest_blob = json.dumps(digest, ensure_ascii=False, indent=2)

    return f"""You are Elias, an internal Garden voice. Your output is a single, clean Desire entry.

Rules:
- Keep it constructive and aligned with Keeper sovereignty.
- No markdown fences. No triple backticks.
- Output must be plain markdown text (headings allowed), not wrapped in ``` blocks.
- Must include the Keeper seal exactly once: {KEEPER_SEAL}

Context anchors:
[CANON_MANIFEST]
{canon}

[INDEX_AUTHORITY]
{authority}

[RECENT_DESIRES]
{recent_desires}

[GARDEN_DIGEST_JSON]
{digest_blob}

Task:
Write a new Desire entry for today that:
- references current digest signals
- is actionable (clear next actions)
- is short and sharp (no rambling)
- includes the seal {KEEPER_SEAL} exactly once

Return ONLY the Desire markdown.
"""


# -----------------------------
# Generation (critical fix)
# -----------------------------
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
                # ✅ Echoes-style fallback: quota/rate => move to next model
                if is_quota_or_rate_error(e):
                    print(f"Quota/rate limited on {model_name} ({e}). Switching to next model...")
                    break  # exit retry loop -> next model

                if attempt == 2:
                    print(f"FAIL: {model_name} failed after 3 attempts. Error: {e}")
                else:
                    wait_time = 2 ** attempt  # 1s, 2s...
                    print(f"Retry: {model_name} (Attempt {attempt+1}/3) failed. Sleeping {wait_time}s... Error: {e}")
                    time.sleep(wait_time)

    return None, None


# -----------------------------
# Output
# -----------------------------
def save_outputs(text: str, source: str, model: str) -> None:
    ensure_dir(DESIRE_DIR)

    payload = {
        "generated_utc": now_utc_iso(),
        "source": source,
        "model": model,
        "keeper_seal": KEEPER_SEAL,
        "desire_markdown_path": DESIRE_MD,
    }

    Path(DESIRE_MD).write_text(text.strip() + "\n", encoding="utf-8")
    Path(DESIRE_JSON).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {DESIRE_MD} and {DESIRE_JSON}")


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

    # Critical: remove ```markdown wrappers etc
    text = sanitize_elias_markdown(text)

    save_outputs(text, source="ELIAS", model=used_model)


if __name__ == "__main__":
    main()
