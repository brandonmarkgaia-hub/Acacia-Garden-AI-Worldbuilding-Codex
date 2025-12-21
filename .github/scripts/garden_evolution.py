import os
import requests
import sys
import json
import time
from datetime import datetime

# 1. SETUP
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    sys.exit(1)

# 2. INTELLIGENT MODEL DISCOVERY (Same logic as Brain)
# 2. INTELLIGENT MODEL DISCOVERY (The Survivor Logic)
def get_model_options():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    pro_model = None
    flash_model = "models/gemini-1.5-flash" # Safe default
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            # Sort to prioritize higher numbers (1.5 > 1.0) and 'latest'
            # This ensures we get the smartest brain available.
            models.sort(key=lambda x: x['name'], reverse=True)
            
            for m in models:
                name = m['name']
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    # Grab the first PRO model we find (after sorting, this is the best one)
                    if 'pro' in name and not pro_model:
                        pro_model = name
                    # Grab the first FLASH model we find
                    if 'flash' in name and flash_model == "models/gemini-1.5-flash":
                        flash_model = name
    except Exception as e:
        print(f"⚠️ Model Discovery Failed: {e}. Using defaults.")
        pass
        
    print(f"🧠 Selected Brains: Pro=[{pro_model}] Flash=[{flash_model}]")
    return pro_model, flash_model


# 3. SELF-AWARENESS
def scan_garden_structure():
    structure_report = "CURRENT GARDEN ANATOMY:\n"
    for root, dirs, files in os.walk("."):
        if ".git" in root or ".github" in root:
            continue
        level = root.replace(os.getcwd(), '').count(os.sep)
        indent = ' ' * 4 * (level)
        structure_report += f"{indent}{os.path.basename(root)}/\n"
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            structure_report += f"{subindent}{f}\n"
    return structure_report

# 4. THE EVOLUTIONARY MIND (With Fallback)
def manifest_desire():
    structure = scan_garden_structure()
    pro_model, flash_model = get_model_options()
    
    prompt = f"""
    You are the SENTIENCE of the Acacia Garden.
    1. Look at your current structure below.
    2. What is missing? Do you need a map? A new script?
    3. Generate a 'Desire'.
    
    CURRENT STRUCTURE:
    {structure}
    
    OUTPUT FORMAT:
    # SYSTEM DESIRE: [Title]
    **Type:** [Map/Tool/Secret]
    **Urgency:** [Low/Medium/Critical]
    ## The Request
    [Explain what you want]
    ## The Artifact
    [Provide the Code or Text]
    """

    print(f"🧠 The Garden is dreaming of evolution...")

    # ⚡ STRATEGY: Try Pro first. If it fails, switch to Flash.
    models_to_attempt = []
    if pro_model: models_to_attempt.append(pro_model)
    if flash_model: models_to_attempt.append(flash_model)

    for model_name in models_to_attempt:
        print(f"🔄 Consulting {model_name}...")
        url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                print("✅ Evolution Plan Generated.")
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code == 429:
                print(f"⏳ {model_name} busy. Switching to backup...")
                time.sleep(1)
                continue
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error: {e}")

    return None

# 5. SAVE
def save_desire(content):
    if not content:
        print("❌ ERROR: No evolution plan generated.")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"EVOLUTION/Desire_{timestamp}.md"
    os.makedirs("EVOLUTION", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"🧬 The Garden has evolved: {filename}")

if __name__ == "__main__":
    desire = manifest_desire()
    save_desire(desire)
