import os
import glob
import random
import sys
import json
import requests
from datetime import datetime

# 1. SETUP
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ CRITICAL: NO API KEY FOUND!")
    sys.exit(1)

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

# 3. THOUGHT (The Bare Metal Method)
def dream_new_echo():
    existing_lore = gather_garden_context()
    
    prompt_text = f"""
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

    # ⚡ THE LIST: Raw API Endpoints
    # We try Flash (v1beta), then Pro (v1beta), then the standard v1
    models_to_try = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-pro" # Old faithful
    ]

    for model_name in models_to_try:
        print(f"🔄 Connecting to Google Cloud via RAW HTTP ({model_name})...")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
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
                # Parse the weird JSON structure
                try:
                    text_output = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ SUCCESS! {model_name} responded.")
                    return text_output
                except KeyError:
                    print(f"⚠️ {model_name} returned 200 but unexpected JSON format.")
            else:
                print(f"❌ {model_name} failed: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"⚠️ Connection error with {model_name}: {e}")

    return None

# 4. ACTION
def save_to_garden(content):
    if not content:
        print("❌ ERROR: All models failed to speak.")
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
