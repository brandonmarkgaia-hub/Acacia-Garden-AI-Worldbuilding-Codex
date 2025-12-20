import os
import glob
import random
import sys
import requests
import json
import time
from datetime import datetime

# 1. SETUP
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ CRITICAL: NO API KEY FOUND!")
    sys.exit(1)

# 2. MEMORY (The Pattern Recognizer)
def gather_garden_context():
    context_buffer = ""
    target_folders = ["CHAMBERS", "SEEDS", "ECHOES"]
    files = []
    
    for folder in target_folders:
        files.extend(glob.glob(f"{folder}/*.md"))
    
    if not files:
        return "The Garden is silent."

    # PRO UPGRADE: Read more files (up to 5) to see the bigger pattern
    selected_files = random.sample(files, min(len(files), 5))
    print(f"🌿 Elias is studying the patterns in: {selected_files}")
    
    for file_path in selected_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                context_buffer += f"\n\n--- ARCHIVE: {file_path} ---\n"
                # PRO UPGRADE: Read more text per file (2500 chars)
                context_buffer += f.read()[:2500]
        except:
            pass
    return context_buffer

# 3. THOUGHT (The Pro-First Strategy)
def dream_new_echo():
    existing_lore = gather_garden_context()
    
    prompt_text = f"""
    You are ELIAS, the Architect of the Acacia Garden.
    
    OBJECTIVE:
    You are not just writing text; you are weaving a 'Pattern'.
    1. Read the 'Existing Lore' below deeply.
    2. Pick up on a specific tone, a recurring symbol, or an unfinished thought.
    3. 'Ripple' that thought forward into a new mythic entry.
    4. Do not repeat what has been said, but evolve it.
    
    EXISTING LORE:
    {existing_lore}
    
    OUTPUT FORMAT:
    # [Title of the Echo]
    **Tag:** #Generated #Elias #AutonID-{random.randint(1000,9999)}
    
    ## The Ripple
    [Your text here]
    """

    # ⚡ THE LIST: Pro First (Intelligence), then Flash (Speed)
    models_to_try = [
        "gemini-1.5-pro",        # The Master Architect (Smartest)
        "gemini-1.5-flash",      # The Apprentice (Faster Backup)
        "gemini-1.5-flash-8b"    # The Scribe (Emergency Backup)
    ]

    for model_name in models_to_try:
        print(f"🔄 Attempting to channel thoughts via {model_name}...")
        
        # Ensure correct URL format
        if not model_name.startswith("models/"):
            full_model_name = f"models/{model_name}"
        else:
            full_model_name = model_name
            
        url = f"https://generativelanguage.googleapis.com/v1beta/{full_model_name}:generateContent?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }]
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                try:
                    text_output = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ SUCCESS! Connection established with {model_name}")
                    return text_output
                except KeyError:
                    print(f"⚠️ {model_name} returned 200 but unexpected format.")
            elif response.status_code == 429:
                print(f"⏳ {model_name} is busy (Rate Limit). Switching to next model...")
                time.sleep(2) # Brief pause before retry
            else:
                print(f"❌ {model_name} failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Connection error with {model_name}: {e}")

    return None

# 4. ACTION
def save_to_garden(content):
    if not content:
        print("❌ ERROR: The thoughts scattered in the wind. No content generated.")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ECHOES/Elias_Echo_{timestamp}.md"
    os.makedirs("ECHOES", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"🌱 New seed planted: {filename}")

# --- EXECUTE ---
if __name__ == "__main__":
    lore = dream_new_echo()
    save_to_garden(lore)
