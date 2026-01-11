#!/usr/bin/env python3
import os
import argparse
import datetime as dt
from pathlib import Path
import requests 

# --- CONFIGURATION ---
ROOT = Path(__file__).resolve().parents[2]
NOVELLAS_DIR = ROOT / "docs" / "Novellas" / "The_Stone_And_The_Star"
NOVELLAS_DIR.mkdir(parents=True, exist_ok=True)

# We use the STATUS and INDEX to ground the story in reality
STATUS_PATH = ROOT / "STATUS.json"
LORE_PATH = ROOT / "docs" / "Archives" / "CODEX_MONOLITH.html" 

def read_file(p: Path, limit: int = 50000) -> str:
    if not p.exists(): return ""
    try:
        return p.read_text(encoding="utf-8", errors="ignore")[:limit]
    except: return ""

def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key: raise SystemExit("Missing GEMINI_API_KEY")

    # ARGUMENTS: What chapter are we writing?
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", default="01", help="Chapter number (e.g. 01)")
    parser.add_argument("--title", default="The_Boy_Who_Talked_To_Code", help="Chapter Title")
    parser.add_argument("--focus", default="Origins", help="What happens in this chapter?")
    args = parser.parse_args()

    # --- THE ROTHFUSS PROMPT ---
    # This instructs the AI to write with high literary quality.
    prompt_text = f"""
    You are the Master Storyteller of the Acacia Garden.
    
    STYLE GUIDE:
    - Tone: "The Name of the Wind" by Patrick Rothfuss.
    - Qualities: Lyrical, precise, melancholic but wondrous.
    - Magic System: The "Code" and "Files" are the magic. Treat "Coding" like "Sympathy". 
      (Linking two things to transfer energy). Treat "Naming" like "Root Access".
    - Protagonist: The Keeper (Brandon). A figure of legend who is also deeply human.
    
    CONTEXT (The Lore of the World):
    [STATUS] {read_file(STATUS_PATH)}
    
    TASK:
    Write CHAPTER {args.chapter}: "{args.title}".
    Focus: {args.focus}
    
    REQUIREMENTS:
    - Write at least 2,000 words.
    - Show, don't tell.
    - Use the "Files" (Chambers/Echoes) as physical locations or artifacts in the story.
    - End on a hook.
    """.strip()

    # USE PRO MODEL FOR WRITING (Better Prose)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "temperature": 0.8,     # Higher creativity
            "maxOutputTokens": 8192 # MAXIMUM allowed text output
        }
    }

    print(f"✍️  Scribing Chapter {args.chapter}: {args.title}...")
    response = requests.post(url, json=payload, timeout=120) # Longer timeout for writing
    
    if response.status_code != 200:
        print(f"❌ Error: {response.text}")
        return

    data = response.json()
    try:
        story_text = data['candidates'][0]['content']['parts'][0]['text']
        
        # Save the Chapter
        filename = f"Chapter_{args.chapter}_{args.title}.md"
        out_path = NOVELLAS_DIR / filename
        out_path.write_text(f"# {args.title}\n\n{story_text}", encoding="utf-8")
        
        print(f"✅ Chapter written to: {out_path}")
        print("   Status: Masterpiece Candidate.")
        
    except Exception as e:
        print(f"❌ Formatting Error: {e}")

if __name__ == "__main__":
    main()
