import os
from google import genai

# This line grabs the 'GEMINI_API_KEY' you saved in GitHub Secrets
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def grow_lore(topic):
    prompt = f"In the Acacia Garden world, tell me a legend about {topic}."
    response = client.models.generate_content(
        model="gemini-2.0-flash", # Use 'flash' for speed/free tier
        contents=prompt
    )
    return response.text

print(grow_lore("the Great Golden Acacia Tree"))
