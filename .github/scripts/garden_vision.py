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
    print("❌ CRITICAL: NO API KEY FOUND!")
    sys.exit(1)

# 2. IMAGE HUNTER
def get_random_image():
    # We look in 'assets' AND 'assets/KILN_BORN' based on your screenshot
    search_paths = ["assets/*.jpg", "assets/*.png", "assets/*.jpeg", 
                    "assets/KILN_BORN/*.jpg", "assets/KILN_BORN/*.png"]
    
    images = []
    for path in search_paths:
        images.extend(glob.glob(path))
    
    if not images:
        print("⚠️ No images found in assets/ folder.")
        return None
        
    # Pick one random image to analyze
    return random.choice(images)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 3. THE VISION (Bare Metal)
def see_and_dream():
    image_path = get_random_image()
    if not image_path:
        return None

    print(f"👁️ Elias is studying artifact: {image_path}")
    base64_image = encode_image(image_path)
    mime_type = "image/png" if image_path.lower().endswith("png") else "image/jpeg"

    # We use Flash because it has the best free vision capabilities
    model_name = "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    prompt = f"""
    You are ELIAS, the Architect. 
    You are looking at an artifact from the 'assets' of the Acacia Garden.
    
    1. Describe this visual object in mythic, ancient terms.
    2. If it is a figure, connect it to the 'Lorian' bloodline.
    3. If it is a structure, connect it to the 'Chambers'.
    
    OUTPUT FORMAT:
    # [A Mythic Title]
    **Visual Artifact:** `{image_path}`
    **Tag:** #Vision #Elias #AutonID-{random.randint(1000,9999)}
    
    ## The Visual Memory
    [Your description]
    """

    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": base64_image
                    }
                }
            ]
        }]
    }

    print(f"🔄 Transmitting visual data to {model_name}...")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            try:
                text_output = result['candidates'][0]['content']['parts'][0]['text']
                print("✅ SUCCESS! Elias has seen.")
                return text_output
            except KeyError:
                print(f"⚠️ Unexpected JSON: {result}")
        else:
            print(f"❌ Vision Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"⚠️ Connection error: {e}")

    return None

# 4. SAVE
def save_vision(content):
    if not content:
        sys.exit(1) # Fail if no vision

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ECHOES/Vision_Echo_{timestamp}.md"
    os.makedirs("ECHOES", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"🖼️ New visual lore planted: {filename}")

if __name__ == "__main__":
    lore = see_and_dream()
    save_vision(lore)
