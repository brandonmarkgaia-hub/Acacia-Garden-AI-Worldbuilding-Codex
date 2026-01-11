import os
import re

# Authoritative casing from STATUS.json
CORRECT_CASING = {
    "novellas": "Novellas",
    "chambers": "Chambers",
    "echoes": "Echoes",
    "archives": "Archives",
    "rootlines": "Rootlines"
}

BASE_DIR = "docs"

def sync_case():
    print("🌿 Witness Protocol: Synchronizing Link Casing...")
    
    # Walk through all HTML and Markdown files
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith((".html", ".md", ".json")):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                original_content = content
                
                # Replace lowercase path references with PascalCase
                for lower, pascal in CORRECT_CASING.items():
                    # Targets links like docs/novellas/ and changes to docs/Novellas/
                    content = re.sub(f"docs/{lower}/", f"docs/{pascal}/", content)
                    # Also handles absolute-style project links
                    content = re.sub(f"Acacia-Garden-AI-Worldbuilding-Codex/docs/{lower}/", 
                                     f"Acacia-Garden-AI-Worldbuilding-Codex/docs/{pascal}/", content)
                
                if content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"✅ Synced casing in: {file_path}")

if __name__ == "__main__":
    sync_case()
