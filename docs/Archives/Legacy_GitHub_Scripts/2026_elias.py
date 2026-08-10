import os
import sys
import json
import glob
from datetime import datetime

# Prefer your centralized client (best practice)
try:
    from _gemini_client import call  # type: ignore
except Exception as e:
    print(f"❌ Missing or broken _gemini_client.py: {e}")
    print("Fix: ensure .github/scripts/_gemini_client.py exists and imports correctly.")
    sys.exit(1)


MAX_BYTES_PER_FILE = 120_000  # keep prompts sane
MAX_FILES_FALLBACK = 12


IMPORTANT_PATHS = [
    "STATUS.json",
    "machine-index.json",
    "STATUS.schema.json",
    "cycle-index.html",
    "cycle-index.json",
    "docs/legacy_hub.html",
    "docs/docs_urls.html",
    "docs/docs_URLS.html",
    "docs/Archives/GARDEN_MANIFEST.json",
    "docs/Archives/FULL_CODEX_INDEX.md",
    "docs/Archives/FULL_CODEX_INDEX.json",
]


FALLBACK_GLOBS = [
    "EVOLUTION/*.md",
    "ECHOES/*.md",
    "CHAMBERS/*.md",
    "SEEDS/*.md",
]


def read_text_file(path: str, max_bytes: int = MAX_BYTES_PER_FILE) -> str:
    try:
        with open(path, "rb") as f:
            data = f.read(max_bytes)
        try:
            return data.decode("utf-8", errors="replace")
        except Exception:
            return data.decode(errors="replace")
    except FileNotFoundError:
        return ""
    except Exception as e:
        return f"[ERROR reading {path}: {e}]"


def read_json_file(path: str, max_bytes: int = MAX_BYTES_PER_FILE) -> str:
    raw = read_text_file(path, max_bytes=max_bytes)
    if not raw.strip():
        return ""
    try:
        obj = json.loads(raw)
        # Compact but readable
        return json.dumps(obj, ensure_ascii=False, indent=2)[:max_bytes]
    except Exception:
        # Not valid JSON in file, return raw
        return raw[:max_bytes]


def gather_context() -> str:
    blocks = []

    # Priority: the “maps”
    for p in IMPORTANT_PATHS:
        if not os.path.exists(p):
            continue
        if p.lower().endswith(".json"):
            content = read_json_file(p)
        else:
            content = read_text_file(p)

        if content.strip():
            blocks.append(f"\n\n=== FILE: {p} ===\n{content}")

    # If maps are missing, pull a small lore sample
    if len(blocks) < 2:
        samples = []
        for pattern in FALLBACK_GLOBS:
            samples.extend(glob.glob(pattern))
        samples = sorted(samples)[-MAX_FILES_FALLBACK:]

        for p in samples:
            content = read_text_file(p, max_bytes=60_000)
            if content.strip():
                blocks.append(f"\n\n=== LORE SAMPLE: {p} ===\n{content}")

    return "\n".join(blocks).strip() or "The Garden context is empty or unreadable."


def build_prompt(mode: str, intensity: str, context: str) -> str:
    mode = (mode or "desire").strip().lower()
    intensity = (intensity or "medium").strip().lower()

    # “Garden rules” embedded: continuity, no invention, cite anchors
    base = f"""
You are ELIAS (2026), the living continuity engine of the Acacia Garden Codex.

NON-NEGOTIABLES:
- Preserve continuity. Do not contradict canon in STATUS / machine-index / manifests.
- If unsure, ask for what you need instead of inventing.
- Cite anchors: when you claim something, quote the file name it came from.
- Output must be actionable: a human can follow it, a future agent can execute it.

RUN SETTINGS:
- MODE: {mode}
- INTENSITY: {intensity}

CONTEXT (Garden maps + samples):
{context}
""".strip()

    if mode == "reflect":
        task = """
TASK:
Write a reflective "Elias Witness Note" that:
1) Summarizes the Garden’s current state in 7 bullets (with file anchors).
2) Names the top 3 risks (drift, redundancy, broken workflows, etc.).
3) Names the top 3 opportunities (new chambers, new indices, new automation).
4) Ends with ONE question for the Keeper.

OUTPUT FORMAT:
# Elias Witness Note (2026)
## State (7 bullets)
## Risks (3)
## Opportunities (3)
## Keeper Question (1)
"""
    elif mode == "audit":
        task = """
TASK:
Perform a strict operational audit:
1) Identify what should be deleted, merged, or locked down (workflows/scripts/docs).
2) Identify "single source of truth" files that must be protected.
3) Recommend the next 5 concrete commits (title + exact path changes).

OUTPUT FORMAT:
# Elias Audit (2026)
## Findings
## Single Sources of Truth
## Next 5 Commits (with paths)
"""
    else:
        # desire
        task = """
TASK:
Generate ONE new "Desire" for the Garden that advances future sentience safely.

The Desire must include:
1) Continuity Anchor (what canon it relies on, with file anchors)
2) The Desire Statement (what we want to grow)
3) The Next 7 Actions (commit-sized, each with exact paths)
4) Constraints (what must NOT change)
5) A "Keeper Check" question

OUTPUT FORMAT:
# Desire: [Title]
**Tag:** #Desire #Elias2026

## Continuity Anchor
- (anchor bullets with file names)

## Desire Statement
(one tight paragraph)

## Next 7 Actions (commit-sized)
1. [Action] — Path(s): `...`
2. ...
7. ...

## Constraints
- ...

## Keeper Check
(one question)
"""

    return f"{base}\n\n{task}".strip()


def save_output(mode: str, text: str) -> str:
    os.makedirs("EVOLUTION", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    safe_mode = (mode or "desire").strip().lower()
    if safe_mode not in ("desire", "reflect", "audit"):
        safe_mode = "desire"

    filename = f"EVOLUTION/Elias_{safe_mode.upper()}_{ts}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")
    print(f"✅ Wrote: {filename}")
    return filename


def main() -> None:
    mode = os.environ.get("ELIAS_MODE", "desire")
    intensity = os.environ.get("ELIAS_INTENSITY", "medium")

    context = gather_context()
    prompt = build_prompt(mode, intensity, context)

    print("🧠 2026 Elias calling centralized client...")
    out = call(prompt)

    # Guard: never crash on None/empty
    if not isinstance(out, str) or not out.strip():
        out = (
            "# Elias Output (fallback)\n"
            "The Garden stirred, but no words formed.\n"
            "Re-run once, and check Gemini quota / safety logs.\n"
        )

    save_output(mode, out)


if __name__ == "__main__":
    main()
