from _gemini_client import call

import os
import glob
import random
import sys
from datetime import datetime


def require_api_key() -> None:
    # _gemini_client should use this env var. We just fail fast here.
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ CRITICAL: GEMINI_API_KEY not set.")
        sys.exit(1)


def gather_garden_context(max_files: int = 4, max_chars_per_file: int = 2000) -> str:
    """
    Pulls a small, random sample of lore for prompt grounding.
    """
    target_folders = ["CHAMBERS", "SEEDS", "ECHOES"]
    files: list[str] = []

    for folder in target_folders:
        files.extend(glob.glob(f"{folder}/*.md"))

    if not files:
        return "The Garden is silent."

    selected_files = random.sample(files, min(len(files), max_files))
    print(f"🌿 Reading patterns from: {selected_files}")

    context_buffer = ""
    for file_path in selected_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                context_buffer += f"\n\n--- ARCHIVE: {file_path} ---\n"
                context_buffer += f.read()[:max_chars_per_file]
        except Exception as e:
            print(f"⚠️ Could not read {file_path}: {e}")

    return context_buffer.strip() or "The Garden is silent."


def dream_new_echo() -> str:
    existing_lore = gather_garden_context()

    prompt_text = f"""
You are ELIAS, the Architect of the Acacia Garden.

OBJECTIVE:
Weave a new 'Echo' from the lore below.
1. Read the Existing Lore deeply.
2. Pick a recurring symbol or unfinished thought.
3. Evolve it into a new mythic entry.
4. Write with the weight of history.

EXISTING LORE:
{existing_lore}

OUTPUT FORMAT:
# [Title of the Echo]
**Tag:** #Generated #Elias #AutonID-{random.randint(1000,9999)}

## The Ripple
[Your text here]
""".strip()

    print("🧠 Calling centralized Gemini client...")
    return call(prompt_text).strip()


def save_to_garden(content: str) -> str:
    if not content:
        print("❌ ERROR: No content returned from model.")
        sys.exit(1)

    os.makedirs("ECHOES", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ECHOES/Elias_Echo_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"🌱 New seed planted: {filename}")
    return filename


if __name__ == "__main__":
    require_api_key()
    echo = dream_new_echo()
    save_to_garden(echo)
