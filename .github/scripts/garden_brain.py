import os
import glob
import random
import sys
from datetime import datetime
import google.generativeai as genai # The Classic Library

# 1. SETUP
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ CRITICAL: NO API KEY FOUND!")
    sys.exit(1)

# Configure the old-school way (It just works)
genai.configure(api_key=api_key)

# 2. MEMORY
def gather_garden_context():
    context_buffer = ""
    target_folders = ["CHAMBERS", "SEEDS", "ECHOES"]
    files = []
    
    for folder in target_folders:
        files.extend(glob.glob(f"{folder}/*.md"))
    
    if not files:
        return "The Garden is silent."

    # Keep it light: 3 files max
    selected_files = random.sample(files, min(len(files), 3))
    print(f"🌿 Reading context from: {selected_files}")
    
    for file_path in selected_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                context_buffer += f"\n\n--- FILE: {file_path} ---\n"
                context_buffer += f.read()[:1500]
        except:
            pass
    return context_buffer

# 3. THOUGHT
def dream_new_echo():
    existing_lore = gather_garden_context()
    
    # We use the standard 1.5 Flash. The Classic SDK knows where to find it.
    model = genai.GenerativeModel("gemini-1.5-flash")
    
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

    print(f"⚡ Elias is thinking (Classic Mode)...")
    
    try:
        # The classic method call
        response = model.generate_content(prompt)
        
        # Check if response was blocked (safety filters)
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            print(f"⚠️ Blocked: {response.prompt_feedback.block_reason}")
            return None
            
        return response.text
    except Exception as e:
        print(f"❌ Failed: {e}")
        # Last ditch effort: Try the legacy 'pro' model if flash fails
        try:
            print("🔄 Retrying with Gemini Pro...")
            backup_model = genai.GenerativeModel("gemini-pro")
            response = backup_model.generate_content(prompt)
            return response.text
        except:
            return None

# 4. ACTION
def save_to_garden(content):
    if not content:
        print("❌ ERROR: Elias remained silent.")
        sys.exit(1)

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
