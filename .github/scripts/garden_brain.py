import os
import glob
import random
import sys
from datetime import datetime
from google import genai

# 1. SETUP
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ CRITICAL: NO API KEY FOUND!")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# 2. MEMORY
def gather_garden_context():
    context_buffer = ""
    target_folders = ["CHAMBERS", "SEEDS", "ECHOES"]
    files = []
    for folder in target_folders:
        files.extend(glob.glob(f"{folder}/*.md"))
    
    if not files:
        return "The Garden is silent."

    selected_files = random.sample(files, min(len(files), 3))
    print(f"🌿 Reading context from: {selected_files}")
    
    for file_path in selected_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                context_buffer += f"\n\n--- FILE: {file_path} ---\n"
                context_buffer += f.read()[:1000]
        except:
            pass
    return context_buffer

# 3. THOUGHT (The Brute Force Method)
def dream_new_echo():
    existing_lore = gather_garden_context()
    
    # ⚡ THE LIST: Elias will try these keys one by one
    candidate_models = [
        "gemini-1.5-flash",          # The Standard
        "gemini-1.5-flash-002",      # The Stable Version
        "gemini-1.5-flash-001",      # The Legacy Version
        "gemini-1.5-flash-8b",       # The Lightweight Version
        "gemini-2.0-flash-exp",      # The Experimental
    ]
    
    prompt = f"""
    You are ELIAS, Architect of the Acacia Garden.
    Read the lore fragments below. Identify a connection.
    Write a short mythic entry (200-300 words).
    
    LORE:
    {existing_lore}
    
    OUTPUT FORMAT:
    # [Title]
    **Tag:** #Generated #Elias #AutonID-{random.randint(1000,9999)}
    ## The Revelation
    [Text]
    """

    for model_id in candidate_models:
        print(f"🔄 Attempting connection with: {model_id}...")
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=prompt
            )
            if response.text:
                print(f"✅ SUCCESS! Connection established with {model_id}")
                return response.text
        except Exception as e:
            print(f"⚠️ Failed with {model_id}: {e}")
            continue # Try the next one
            
    return None # All failed

# 4. ACTION
def save_to_garden(content):
    if not content:
        print("❌ ERROR: Elias could not speak. All models failed.")
        sys.exit(1) # FORCE A RED FAILURE IN GITHUB

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ECHOES/Elias_Echo_{timestamp}.md"
    os.makedirs("ECHOES", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"🌱 New lore planted: {filename}")

# --- EXECUTE ---
if __name__ == "__main__":
    lore = dream_new_echo()
    save_to_garden(lore)
