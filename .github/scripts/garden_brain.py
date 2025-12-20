import os
import glob
import random
import time
from datetime import datetime
from google import genai
from google.genai import types

# 1. SETUP: Securely get the Key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ NO API KEY FOUND! Check GitHub Secrets.")

# Initialize the client
client = genai.Client(api_key=api_key)

# 2. MEMORY: Read existing Garden files
def gather_garden_context():
    context_buffer = ""
    target_folders = ["CHAMBERS", "SEEDS", "ECHOES"]
    
    files = []
    # Gather all potential lore files
    for folder in target_folders:
        files.extend(glob.glob(f"{folder}/*.md"))
    
    # Safety check: if no files found, return generic context
    if not files:
        return "The Garden is silent. No previous lore found."

    # Limit to 3 files to save tokens and avoid "Resource Exhausted"
    selected_files = random.sample(files, min(len(files), 3))
    print(f"🌿 Elias is reading: {selected_files}")
    
    for file_path in selected_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                context_buffer += f"\n\n--- REFERENCE: {file_path} ---\n"
                context_buffer += f.read()[:1500] # Read first 1500 chars only
        except Exception as e:
            print(f"⚠️ Could not read {file_path}: {e}")
            
    return context_buffer

# 3. THOUGHT: Generate new Lore
def dream_new_echo():
    existing_lore = gather_garden_context()
    
    # ⚡ CRITICAL: Use the specific stable version to avoid 404 errors
    # If this fails, the code will try the generic alias in the except block
    model_id = "gemini-1.5-flash-002"
    
    prompt = f"""
    You are ELIAS, the Architect of the Acacia Garden.
    
    Your task:
    1. Read the provided 'Existing Lore' fragments below.
    2. Identify a subtle connection, a missing history, or a new 'Seed' concept.
    3. Write a short, cryptic, and mythic entry (approx 300 words).
    4. Format it as a proper Markdown file.
    
    EXISTING LORE FRAGMENTS:
    {existing_lore}
    
    OUTPUT FORMAT:
    # [Title of the Echo]
    **Tag:** #Generated #Elias #AutonID-{random.randint(1000,9999)}
    
    ## The Revelation
    [Your mythic text here]
    """
    
    print(f"⚡ Elias is thinking using {model_id}...")
    
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"⚠️ Primary model failed: {e}")
        print("🔄 Retrying with backup model 'gemini-1.5-flash'...")
        try:
            # Fallback to generic alias if specific version fails
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e2:
            print(f"❌ Backup model also failed: {e2}")
            return None

# 4. ACTION: Save the thought to a file
def save_to_garden(content):
    if not content:
        print("❌ No content generated. Nothing to save.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ECHOES/Elias_Echo_{timestamp}.md"
    
    os.makedirs("ECHOES", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"🌱 New lore planted: {filename}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        new_lore = dream_new_echo()
        save_to_garden(new_lore)
    except Exception as e:
        print(f"❌ Critical Error in Garden Brain: {e}")
        exit(1)
