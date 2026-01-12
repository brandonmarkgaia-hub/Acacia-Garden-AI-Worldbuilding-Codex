#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

# CONFIGURATION
ROOT_DIR = Path(__file__).resolve().parents[2] # The Repo Root
DOCS_DIR = ROOT_DIR / "docs"
# Folders to NEVER touch (Safety List)
IGNORE_DIRS = {".git", ".github", "docs", "assets", "images", "node_modules", "_site"}

def get_docs_mapping():
    """
    Creates a map of {lowercase_name: actual_path} for all folders in docs/
    Example: {'eidolon': Path('docs/Eidolon'), 'chambers': Path('docs/Chambers')}
    """
    if not DOCS_DIR.exists():
        print("❌ Critical: docs/ folder not found.")
        return {}
    
    mapping = {}
    for item in DOCS_DIR.iterdir():
        if item.is_dir():
            mapping[item.name.lower()] = item
    return mapping

def safe_move_merge(src_dir: Path, dest_dir: Path):
    """
    Moves all files from src_dir to dest_dir.
    Renames on collision to prevent data loss.
    """
    print(f"   ↳ Merging: {src_dir}  ->  {dest_dir}")
    
    for item in src_dir.iterdir():
        if item.is_file():
            dest_file = dest_dir / item.name
            
            # COLLISION CHECK
            if dest_file.exists():
                # Generate a safe new name
                new_name = f"{item.stem}_root_merge{item.suffix}"
                dest_file = dest_dir / new_name
                print(f"     ⚠️ Collision! Renaming to: {new_name}")
            
            # Move the file
            shutil.move(str(item), str(dest_file))
            print(f"     ✅ Moved: {item.name}")
            
        elif item.is_dir():
            # If it's a sub-sub folder, recurse (go deeper)
            sub_dest = dest_dir / item.name
            sub_dest.mkdir(exist_ok=True)
            safe_move_merge(item, sub_dest)
            # Clean up empty sub-folder
            try:
                item.rmdir()
            except:
                pass

def main():
    print("🔍 Scanning Garden for Root/Docs Duplicates...")
    
    docs_map = get_docs_mapping()
    duplicates_found = 0

    # Scan Root for directories
    for item in ROOT_DIR.iterdir():
        if item.is_dir() and item.name not in IGNORE_DIRS:
            
            # Check if this root folder exists in docs (case-insensitive)
            # e.g. Root "EIDOLON" vs Docs "eidolon" key
            root_name_lower = item.name.lower()
            
            if root_name_lower in docs_map:
                target_docs_dir = docs_map[root_name_lower]
                
                print(f"\n🚨 FOUND DUPLICATE: Root/{item.name} matches {target_docs_dir}")
                
                # EXECUTE MERGE
                safe_move_merge(item, target_docs_dir)
                
                # REMOVE ROOT FOLDER (If empty)
                try:
                    item.rmdir()
                    print(f"   🗑️  Cleaned up empty root folder: {item.name}")
                except OSError:
                    print(f"   ⚠️  Could not remove {item.name} (not empty?)")
                
                duplicates_found += 1

    if duplicates_found == 0:
        print("\n✅ No duplicates found. The Garden is tidy.")
    else:
        print(f"\n✨ Process Complete. {duplicates_found} folders merged into docs/.")

if __name__ == "__main__":
    main()
