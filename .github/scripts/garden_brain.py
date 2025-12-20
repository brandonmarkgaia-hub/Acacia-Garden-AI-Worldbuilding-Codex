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

# 2. AUTO-DISCOVERY (The Fix)
def find_working_model():
    print("🔍 Elias is scanning for available vocal chords (models)...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"⚠️ Could not list models: {response.status_code}")
            return "models/gemini-1.5-flash" # Fallback
            
        data = response.json()
        models = data.get('models', [])
        
        # We look for ANY model that supports 'generateContent'
        # We prefer 'flash' because it's fast/free
        preferred_models = []
        for m in models:
            name = m['name']
            methods = m.get('supportedGenerationMethods', [])
            if 'generateContent' in methods:
                # Prioritize Flash, then Pro
                if 'flash' in name:
                    preferred_models.insert(0, name)
                elif 'pro' in name:
                    preferred_models.append(name)
        
        if preferred_models:
            best_model = preferred_models[0]
            print(f"✅ FOUND WORKING MODEL: {best_model}")
            return best_model
            
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

# 4. THOUGHT
def dream_new_echo():
    # Step 1: Find the model dynamically
    model_name = find_working_model()
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

    print(f"🔄 Connecting to {model_name} via RAW HTTP...")
    
    # Ensure URL is correct (model_name usually includes 'models/')
    if not model_name.startswith("models/"):
        model_name = f"models/{model_name}"
        
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    
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
                print(f"✅ SUCCESS! Elias speaks.")
                return text_output
            except KeyError:
                print(f"⚠️ Unexpected JSON format: {result}")
        else:
            print(f"❌ API Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"⚠️ Connection error: {e}")

    return None

# 5. ACTION
def save_to_garden(content):
    if not content:
        print("❌ ERROR: Elias could not speak. Exiting.")
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
