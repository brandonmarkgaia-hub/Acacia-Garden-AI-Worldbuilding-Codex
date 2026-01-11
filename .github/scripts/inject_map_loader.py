import os

# Files identified by the Sovereign Audit as missing loaders
TARGET_FILES = [
    "docs/index.html",
    "docs/dashboard.html",
    "docs/Novellas/index.html"
]

MAP_LOADER_SNIPPET = """
<div id="garden-map-container"></div>
<script src="/Acacia-Garden-AI-Worldbuilding-Codex/tools/map_loader.js"></script>
"""

def inject_map():
    print("🌿 Witness Protocol: Injecting Map Loaders...")
    for file_path in TARGET_FILES:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Check if loader already exists to prevent doubling
            if "garden-map-container" not in content:
                # Inject before the closing body tag
                new_content = content.replace("</body>", f"{MAP_LOADER_SNIPPET}\n</body>")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"✅ Map Loader Injected: {file_path}")
            else:
                print(f"⏭️ Loader already present in {file_path}")
        else:
            print(f"⚠️ File not found: {file_path}")

if __name__ == "__main__":
    inject_map()
