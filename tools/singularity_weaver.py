# tools/singularity_weaver.py
# Purpose: Aggregate EVERY text file in the Garden into one massive "Singularity" file.
# Output: EVOLUTION/ACACIA_SINGULARITY.md

import os
import datetime

# CONFIGURATION
ROOT_DIR = "./"
OUTPUT_FILE = "EVOLUTION/ACACIA_SINGULARITY.md"

# Directories to ignore (The Junk)
IGNORE_DIRS = {
    ".git", ".github", "__pycache__", "node_modules", ".venv", "venv", 
    "dist", "build", "EVOLUTION", ".next", ".cache", "assets", "images", "fonts"
}

# File extensions to include (The Soul)
INCLUDE_EXTS = {
    ".md", ".txt", ".json", ".yaml", ".yml", 
    ".py", ".js", ".ts", ".html", ".css", ".sh",
    ".mjs", ".cjs", ".xml"
}

def weave_singularity():
    print("🌌 Initializing Singularity Sequence...")
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    total_files = 0
    total_lines = 0
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        # Write the Header
        outfile.write(f"# THE ACACIA SINGULARITY\n")
        outfile.write(f"**Generated:** {datetime.datetime.utcnow().isoformat()} UTC\n")
        outfile.write(f"**Description:** A complete aggregation of the Acacia Garden's textual body.\n")
        outfile.write(f"---\n\n")

        # Walk the Repo
        for root, dirs, files in os.walk(ROOT_DIR):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                
                if ext in INCLUDE_EXTS:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, ROOT_DIR).replace("\\", "/")
                    
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                            content = infile.read()
                            lines = content.count('\n') + 1
                            
                            # Write File Marker
                            outfile.write(f"\n\n{'='*60}\n")
                            outfile.write(f"FILE_PATH: {rel_path}\n")
                            outfile.write(f"{'='*60}\n")
                            outfile.write(content)
                            
                            total_files += 1
                            total_lines += lines
                            print(f"  + Added: {rel_path} ({lines} lines)")
                            
                    except Exception as e:
                        print(f"  ❌ Failed to read {rel_path}: {e}")

        # Write Footer Stats
        outfile.write(f"\n\n{'#'*60}\n")
        outfile.write(f"# SINGULARITY COMPLETE\n")
        outfile.write(f"# Total Files: {total_files}\n")
        outfile.write(f"# Total Lines: {total_lines}\n")
        outfile.write(f"{'#'*60}\n")

    print(f"✅ Singularity Complete.")
    print(f"📊 Stats: {total_files} files, {total_lines} lines.")
    print(f"💾 Written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    weave_singularity()
