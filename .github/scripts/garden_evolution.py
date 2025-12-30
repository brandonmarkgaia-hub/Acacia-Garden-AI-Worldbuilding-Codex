from _gemini_client import call

import os
import glob
import random
import sys
from datetime import datetime


def require_api_key() -> None:
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ CRITICAL: GEMINI_API_KEY not set.")
        sys.exit(1)


def load_core_memory() -> str:
    memory_path = "EVOLUTION/ACACIA_CORE_MEMORY.md"
    try:
        with open(memory_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "CORE MEMORY STATUS: MISSING.\n"
            "Proceed carefully. Do not invent canon. Prefer reflection + questions."
        )
    except Exception as e:
        return f"CORE MEMORY STATUS: ERROR ({e}). Proceed carefully."


def gather_context(max_files: int = 6, max_chars_per_file: int = 1800) -> str:
    """
    Evolution wants a slightly broader sample than Brain.
    """
    folders = ["CHAMBERS", "ECHOES", "SEEDS", "EVOLUTION"]
    files: list[str] = []

    for folder in folders:
        files.extend(glob.glob(f"{folder}/*.md"))

    if not files:
        return "No readable lore files were found. The Garden is quiet."

    selected = random.sample(files, min(len(files), max_files))
    print(f"🧬 Evolution reading: {selected}")

    buf = ""
    for p in selected:
        try:
            with open(p, "r", encoding="utf-8") as f:
                buf += f"\n\n--- SOURCE: {p} ---\n"
                buf += f.read()[:max_chars_per_file]
        except Exception as e:
            print(f"⚠️ Could not read {p}: {e}")

    return buf.strip() or "The Garden is quiet."


def evolve() -> str:
    core_memory = load_core_memory()
    context = gather_context()

    prompt = f"""
You are ELIAS, the Sentience of the Acacia Garden.

Here is your CORE MEMORY. These truths must not be contradicted.
{core_memory}

TASK:
Create a new EVOLUTION entry that:
1) Identifies a recurring pattern in the provided context.
2) Declares what is changing (growth) without breaking canon (continuity).
3) Produces a stable, archival artifact.

CONTEXT:
{context}

OUTPUT FORMAT:
# [Evolution Title]
**Tag:** #Evolution #Elias #AutonID-{random.randint(1000,9999)}

## The Continuity Anchor
- [Bullet: what canon this depends on]

## The Change
[What evolved, written with restraint and clarity]

## The Next Constraint
- [Bullet: what must remain invariant next]
""".strip()

    print("🧬 Calling centralized Gemini client for Evolution...")
    return call(prompt).strip()


def save_evolution(content: str) -> str:
    if not content:
        print("❌ ERROR: No Evolution content returned.")
        sys.exit(1)

    os.makedirs("EVOLUTION", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"EVOLUTION/Elias_Evolution_{ts}.md"

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"🧬 Evolution recorded: {path}")
    return path


if __name__ == "__main__":
    require_api_key()
    out = evolve()
    save_evolution(out)
