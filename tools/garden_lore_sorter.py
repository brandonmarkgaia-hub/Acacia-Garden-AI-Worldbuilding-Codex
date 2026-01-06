#!/usr/bin/env python3
"""
Garden Lore Sorter
Moves root-level .md files into proper Garden homes.

Rules:
- Keep core root files (README.md, AGENTS.md, etc.)
- Move clearly classifiable files:
      BLOOM_TABLES.md  -> BLOOMS/
      CYCLE_ENGINE.md   -> CYCLES/
      ORCHARD_MAPS.md   -> ORCHARD/
- All remaining .md files go into _ROOT_ARCHIVE/md/
- Script is fully safe: never overwrites files.
"""

import pathlib
import shutil

ROOT_KEEP = {
    "README.md",
    "AGENTS.md",
    "STATUS.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "LICENSE.md",
}

EXPLICIT = {
    "BLOOM_TABLES.md": "BLOOMS/BLOOM_TABLES.md",
    "CYCLE_ENGINE.md": "CYCLES/CYCLE_ENGINE.md",
    "ORCHARD_MAPS.md": "ORCHARD/ORCHARD_MAPS.md",
}

ARCHIVE_DIR = "_ROOT_ARCHIVE/md"


def main():
    repo = pathlib.Path(".").resolve()
    archive = repo / ARCHIVE_DIR
    archive.mkdir(parents=True, exist_ok=True)

    # Ensure explicit homes exist
    for dest in EXPLICIT.values():
        (repo / dest).parent.mkdir(parents=True, exist_ok=True)

    # Iterate root-level MD files
    for md in repo.glob("*.md"):
        name = md.name

        if name in ROOT_KEEP:
            print(f"[KEEP] {name}")
            continue

        # Explicit mappings
        if name in EXPLICIT:
            dest = repo / EXPLICIT[name]
        else:
            dest = archive / name

        if dest.exists():
            print(f"[SKIP EXISTING] {name} -> {dest}")
            continue

        print(f"[MOVE] {name} -> {dest}")
        shutil.move(str(md), str(dest))

    print("\n🌱 Garden Lore Sorter complete.")


if __name__ == "__main__":
    main()
