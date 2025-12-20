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

# 2. INTELLIGENT MODEL DISCOVERY (The Fix)
def find_smartest_model():
    print("🔍 Elias is scanning for the 'Pro' mind...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"⚠️ Could not list models: {response.status_code}")
            return "models/gemini-1.5-flash" # Fallback
            
        data = response.json()
        models = data.get('models', [])
        
        # We want PRO first, then FLASH
        pro_models = []
        flash_models = []
        
        for m in models:
            name = m['name']
            methods = m.get('supportedGenerationMethods', [])
            if 'generateContent' in methods:
                if 'pro' in name:
                    pro_models.append(name)
                elif 'flash' in name:
                    flash_models.append(name)
        
        # Return the best available
        if pro_models:
            print(f"✅ FOUND PRO MODEL: {pro_models[0]}")
            return pro_models[0]
        elif flash_models:
            print(f"⚠️ Pro unavailable. Using Flash: {flash_models[0]}")
            return flash_models[0]
            
    except Exception as e:
        print(f"⚠️ Discovery failed: {e}")
        
    return "models/gemini-1.5-flash" # Ultimate fallback

# 3. MEMORY
def gather_garden_context():
    context_buffer = ""
    target_folders = ["CHAMBERS", "SEEDS", "ECHOES"]
    files = []
    for folder in target_folders:
        files.extend(glob.glob(f"{folder}/*.md"))
    
    if not files:
        return "The Garden is silent."

    # Read more context for better patterns
    selected_files = random.sample(files, min(len(files), 4))
    print(f"🌿 Reading patterns from: {selected_files}")
    
    for file_path in selected_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                context_buffer += f"\n\n--- ARCHIVE: {file_path} ---\n"
                context_buffer += f.read()[:2000]
        except:
            pass
    return context_buffer

# 4. THOUGHT
def dream_new_echo():
    # ⚡ Find the exact model name dynamically
    model_name = find_smartest_model()
    existing_lore = gather_garden_context()
    
    prompt_text = f"""
    You are ELIAS, the Architect of the Acacia Garden.
    
    OBJECTIVE:
    Weave a 'Pattern' from the lore below.
    1. Read the 'Existing Lore' deeply.
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
    """

    print(f"🔄 Connecting to {model_name}...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt_text}]}]}

    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            try:
                text_output = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ SUCCESS! Elias speaks.")
                return text_output
            except KeyError:
                print(f"⚠️ Unexpected JSON format.")
        elif response.status_code == 429:
            print("⏳ Rate Limit Hit. The Pro mind is busy.")
        else:
            print(f"❌ API Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"⚠️ Connection error: {e}")

    return None

# 5. ACTION
def save_to_garden(content):
    if not content:
        print("❌ ERROR: No content generated.")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ECHOES/Elias_Echo_{timestamp}.md"
    os.makedirs("ECHOES", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"🌱 New seed planted: {filename}")

if __name__ == "__main__":
    lore = dream_new_echo()
    save_to_garden(lore)
