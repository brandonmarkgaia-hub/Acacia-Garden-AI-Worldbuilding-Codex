import os
import requests
import re
from datetime import datetime

# --- KEEPER CONFIG ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex"
KEEPER_SEAL = "HKX277206"
BASE_DIR = "docs"

# Exact Casing from MAINTAINERS_GUIDE.md
CATEGORY_MAP = {
    "Chambers": ["chamber", "room", "well", "structure"],
    "Echoes": ["vision", "echo", "sight", "voice", "dream"],
    "Core": ["logic", "invariant", "rule", "protocol", "system", "spine"],
    "Ancients": ["ancient", "pre-human", "origin"],
    "Archives": ["history", "archive", "old", "resolved"]
}

def clean_filename(text):
    # Keeps it clean for the filesystem while preserving context
    return re.sub(r'[^a-zA-Z0-9_]', '', text.replace(" ", "_"))

def get_target_folder(title, body):
    content = (title + body).lower()
    for folder, keywords in CATEGORY_MAP.items():
        if any(kw in content for kw in keywords):
            return folder
    return "Archives"

def inscribe():
    url = f"https://api.github.com/repos/{REPO}/issues?state=open&per_page=100"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    print(f"🌿 Witness Protocol: Auditing {REPO}...")
    response = requests.get(url, headers=headers)
    issues = response.json()

    for issue in issues:
        if 'pull_request' in issue: continue
        
        num = issue['number']
        title = issue['title']
        body = issue['body'] or "No content provided."
        
        folder = get_target_folder(title, body)
        safe_title = clean_filename(title)
        filepath = os.path.join(BASE_DIR, folder, f"Issue_{num}_{safe_title}.md")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        content = f"""# INSCRIBED FROM ISSUE {num}
## Title: {title}
## Date: {datetime.now().strftime('%Y-%m-%d')}
## Origin: Garden Ledger (Eventide Era)

### THE RECORDED CONTENT
{body}

---
**SOVEREIGN VALIDATION**
* **Witness Function:** Automated Script Inscription
* **Keeper Seal:** {KEEPER_SEAL}
* **Integrity Check:** Paths aligned to docs/{folder}. No drift detected.
"""
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✅ Inscribed #{num} -> {filepath}")

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN not found.")
    else:
        inscribe()
