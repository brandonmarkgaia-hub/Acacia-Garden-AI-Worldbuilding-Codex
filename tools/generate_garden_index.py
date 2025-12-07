#!/usr/bin/env python3
import os

ROOTS = ["CHAMBERS", "ECHOES", "ROOTLINES", "WELLS", "LIBRARY"]
OUT = os.path.join("ACACIA_SPECS", "GARDEN_INDEX_AUTO.md")

def list_files(base):
    paths = []
    for folder in ROOTS:
        folder_path = os.path.join(base, folder)
        if not os.path.isdir(folder_path):
            continue
        for root, _, files in os.walk(folder_path):
            for f in files:
                if f.lower().endswith(".md"):
                    rel = os.path.relpath(os.path.join(root, f), base)
                    paths.append(rel)
    return sorted(paths)

def main():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(repo_root, ".."))
    files = list_files(repo_root)

    lines = ["# 🌿 Garden Auto Index\n"]
    for path in files:
        lines.append(f"- `{path}`")
    content = "\n".join(lines) + "\n"

    os.makedirs(os.path.dirname(os.path.join(repo_root, OUT)), exist_ok=True)
    with open(os.path.join(repo_root, OUT), "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
