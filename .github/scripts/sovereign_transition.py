import os
import requests
import re
import json
from datetime import datetime

# --- KEEPER CONFIG ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex"
KEEPER_SEAL = "HKX277206"
BASE_DIR = "docs"

# Exact Casing/Path Audit from your Garden
CATEGORY_MAP = {
    "Chambers": ["chamber", "room", "well", "structure"],
    "Echoes": ["vision", "echo", "sight", "voice", "dream"],
    "Core": ["logic", "invariant", "rule", "protocol", "system", "spine"],
    "Ancients": ["ancient", "pre-human", "origin"],
    "Archives": ["history", "archive", "old", "resolved"]
}

def clean_filename(text):
    return re.sub(r'[^a-zA-Z0-9_]', '', text.replace(" ", "_"))

def get_target_folder(title, body):
    content = (title + (body or "")).lower()
    for folder, keywords in CATEGORY_MAP.items():
        if any(kw in content for kw in keywords):
            return folder
    return "Archives"

def run_transition():
    url = f"https://api.github.com/repos/{REPO}/issues?state=open&per_page=100"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    print(f"🌿 Witness Protocol: Transitioning {REPO}...")
    response = requests.get(url, headers=headers)
    issues = response.json()

    for issue in issues:
        if 'pull_request' in issue: continue
        
        num = issue['number']
        title = issue['title']
        body = issue['body'] or "No content provided."
        
        # 1. PATH RESOLUTION
        folder = get_target_folder(title, body)
        safe_title = clean_filename(title)
        rel_path = f"{BASE_DIR}/{folder}/Issue_{num}_{safe_title}.md"
        
        os.makedirs(os.path.dirname(rel_path), exist_ok=True)
        
        # 2. FULL CONTENT INSCRIPTION (Copy-Paste Integrity)
        content = f"""# INSCRIBED FROM ISSUE {num}
## Title: {title}
## Date: {datetime.now().strftime('%Y-%m-%d')}
## Origin: Garden Ledger (Eventide Era)

### THE RECORDED CONTENT
{body}

---
**SOVEREIGN VALIDATION**
* **Witness Function:** Automated Sovereign Transition
* **Keeper Seal:** {KEEPER_SEAL}
* **Status:** FIXED IN CHAMBER
"""
        with open(rel_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # 3. POST-INSCRIPTION COMMENT & CLOSURE
        comment_url = f"https://api.github.com/repos/{REPO}/issues/{num}/comments"
        comment_body = {
            "body": f"### 🔒 LEDGER FIXED\nThis entry has been inscribed into the permanent Garden Spine.\n\n**New Path:** `{rel_path}`\n\nVerified under Keeper Seal: **{KEEPER_SEAL}**."
        }
        requests.post(comment_url, headers=headers, json=comment_body)

        close_url = f"https://api.github.com/repos/{REPO}/issues/{num}"
        requests.patch(close_url, headers=headers, json={"state": "closed"})
        
        print(f"✅ Inscribed & Closed #{num} -> {rel_path}")

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN not found.")
    else:
        run_transition()
