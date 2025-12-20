import os
import glob
from google import genai

# Setup the client
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def gather_context():
    """Reads all markdown files in the repo to give Gemini 'memory'."""
    context = ""
    # Looks for all lore files in your repo
    for file in glob.glob("**/*.md", recursive=True):
        with open(file, 'r') as f:
            context += f"\n--- FILE: {file} ---\n" + f.read()
    return context[:15000] # Limits context to stay in free tier

def expand_world():
    lore_context = gather_context()
    
    prompt = f"""
    You are 'Elias', the architect of the Acacia Garden. 
    Based on the existing codex below, identify a 'missing link' or a mystery that hasn't been explained yet.
    Then, write a high-level conceptual entry for it.
    
    EXISTING LORE:
    {lore_context}
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash", # Best for complex reasoning
        contents=prompt
    )
    return response.text

# Run the brain
new_lore = expand_world()
print(f"ELIAS OUTPUT:\n{new_lore}")

# Automatically save the new lore to a file
with open("lore/latest_revelation.md", "w") as f:
    f.write(new_lore)
