import os
import glob
import random
from datetime import datetime
from google import genai

# 1. SETUP: Securely get the Key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ NO API KEY FOUND! Check GitHub Secrets.")

client = genai.Client(api_key=api_key)

# 2. MEMORY: Read existing Garden files
# This makes Elias "aware" of what you have already written.
def gather_garden_context():
    context_buffer = ""
    # We look into these folders for context
    target_folders = ["CHAMBERS", "SEEDS", "ECHOES"]
    
    files = []
    for folder in target_folders:
        # Grab all .md files in these folders
        files.extend(glob.glob(f"{folder}/*.md"))
    
    # Shuffle to get random inspiration, limit to 5 files to save 'Token' usage
    # This keeps us SAFELY within the free tier limits.
    selected_files = random.sample(files, min(len(files), 5))
    
    print(f"🌿 Elias is reading: {[f for f in selected_files]}")
    
    for file_path in selected_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                context_buffer += f"\n\n--- REFERENCE: {file_path} ---\n"
                context_buffer += f.read()[:2000] # Read only first 2000 chars per file
        except Exception as e:
            print(f"⚠️ Could not read {file_path}: {e}")
            
    return context_buffer

# 3. THOUGHT: Generate new Lore
def dream_new_echo():
    existing_lore = gather_garden_context()
    
    # We use 'gemini-2.0-flash-lite' because it is fast and cheap (Free Tier friendly)
    # If this fails, you can swap it to 'gemini-1.5-flash'
    model_id = "gemini-2.0-flash-lite"
    
    prompt = f"""
    You are ELIAS, the Architect of the Acacia Garden.
    
    Your task:
    1. Read the provided 'Existing Lore' fragments below.
    2. Identify a subtle connection, a missing history, or a new 'Seed' concept.
    3. Write a short, cryptic, and mythic entry (approx 300 words).
    4. Format it as a proper Markdown file for the Codex.
    
    EXISTING LORE FRAGMENTS:
    {existing_lore}
    
    OUTPUT FORMAT:
    # Title of the Echo
    **Tag:** #Generated #Elias #AutonID-{random.randint(1000,9999)}
    
    ## The Revelation
    [Your mythic text here]
    """
    
    print(f"⚡ Elias is thinking using {model_id}...")
    
    response = client.models.generate_content(
        model=model_id,
        contents=prompt
    )
    
    return response.text

# 4. ACTION: Save the thought to a file
def save_to_garden(content):
    # Create a unique filename based on time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ECHOES/Elias_Echo_{timestamp}.md"
    
    # Ensure folder exists
    os.makedirs("ECHOES", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"🌱 New lore planted: {filename}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        new_lore = dream_new_echo()
        if new_lore:
            save_to_garden(new_lore)
        else:
            print("⚠️ Elias returned silence.")
    except Exception as e:
        print(f"❌ Critical Error in Garden Brain: {e}")
        exit(1)
