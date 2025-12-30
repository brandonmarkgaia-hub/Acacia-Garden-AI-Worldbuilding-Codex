from _gemini_client import call
import os
import glob
import random
import sys
import base64
import requests
from datetime import datetime

# 1. SETUP
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    sys.exit(1)

# 2. AUTO-DISCOVERY FOR VISION
def find_vision_model():
    print("🔍 Searching for eyes...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        for m in data.get('models', []):
            # Prioritize Flash for vision (it handles images reliably on free tier)
            if 'flash' in m['name'] and 'generateContent' in m['supportedGenerationMethods']:
                return m['name']
    except:
        pass
    return "models/gemini-1.5-flash"

# 3. IMAGE HUNTER
def get_random_image():
    search_paths = ["assets/*.jpg", "assets/*.png", "assets/*.jpeg", 
                    "assets/KILN_BORN/*.jpg", "assets/KILN_BORN/*.png", "GALLERY/*.jpg"]
    images = []
    for path in search_paths:
        images.extend(glob.glob(path))
    if not images:
        return None
    return random.choice(images)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 4. SEE
def see_and_dream():
    image_path = get_random_image()
    if not image_path:
        print("⚠️ No images found.")
        return None

    model_name = find_vision_model()
    print(f"👁️ Analyzing {image_path} using {model_name}...")
    
    base64_image = encode_image(image_path)
    mime_type = "image/png" if image_path.lower().endswith("png") else "image/jpeg"

    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    
    prompt = f"""
    You are ELIAS. Look at this artifact from the Acacia Garden.
    1. Describe it in mythic terms.
    2. Connect it to the 'Lorian' bloodline or 'Chambers'.
    
    OUTPUT FORMAT:
    # [Mythic Title]
    **Visual Artifact:** `{image_path}`
    **Tag:** #Vision #Elias
    
    ## The Visual Memory
    [Description]
    """

    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": mime_type, "data": base64_image}}
            ]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("✅ Vision successful.")
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"❌ Vision Failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error: {e}")

    return None

def save_vision(content):
    if not content:
        sys.exit(1)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ECHOES/Vision_Echo_{timestamp}.md"
    os.makedirs("ECHOES", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    lore = see_and_dream()
    save_vision(lore)
