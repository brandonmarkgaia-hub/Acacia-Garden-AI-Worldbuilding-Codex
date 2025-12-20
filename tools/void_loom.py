# tools/void_loom.py
# Purpose: Identify numerical gaps + ghost references (referenced-but-missing nodes).
# Output: EVOLUTION/VOID_MAP_LATEST.json & EVOLUTION/GHOST_ROOTS_MAP_LATEST.md

import os
import re
import json
from datetime import datetime
from collections import defaultdict

ROOT = "./"
OUT_DIR = "EVOLUTION"
MAX_READ_BYTES = 2 * 1024 * 1024

IGNORE_DIRS = {".git", ".github", "__pycache__", "node_modules", ".venv", "venv", "dist", "build", "EVOLUTION"}
TEXT_EXTS = {".md", ".txt", ".json", ".html", ".yml", ".yaml", ".xml", ".js", ".ts", ".mjs", ".cjs", ".py", ".css"}

FRAG_FILE_RE = re.compile(r"THE_FRAGMENT_(\d+)\.md$", re.IGNORECASE)
ELIAS_FILE_RE = re.compile(r"ELIAS.*?(\d+).*?PLACEHOLDER.*?\.md$", re.IGNORECASE)

FRAG_REF_RE = re.compile(r"(?:THE_)?FRAGMENT[_\s-]*(\d{1,4})", re.IGNORECASE)
ELIAS_REF_RE = re.compile(r"ELIAS[_\s-]*V?\d*[_\s-]*(\d{1,4})", re.IGNORECASE)

def walk_repo(root_dir):
    root_dir = os.path.abspath(root_dir)
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for name in files:
            yield root, name

def relpath(path, root_dir):
    return os.path.relpath(path, root_dir).replace("\\", "/")

def safe_read(path):
    try:
        if os.stat(path).st_size > MAX_READ_BYTES:
            return ""
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""

def gaps(nums):
    if not nums:
        return []
    nums = sorted(set(nums))
    full = set(range(nums[0], nums[-1] + 1))
    return sorted(list(full - set(nums)))

def main():
    root_dir = os.path.abspath(ROOT)
    os.makedirs(OUT_DIR, exist_ok=True)

    fragment_nums = []
    elias_nums = []
    fragment_paths = {}
    elias_paths = {}

    for root, name in walk_repo(root_dir):
        abs_path = os.path.join(root, name)
        rel = relpath(abs_path, root_dir)

        m = FRAG_FILE_RE.match(name)
        if m:
            n = int(m.group(1))
            fragment_nums.append(n)
            fragment_paths[n] = rel
            continue

        m = ELIAS_FILE_RE.match(name)
        if m:
            n = int(m.group(1))
            elias_nums.append(n)
            elias_paths[n] = rel
            continue

    referenced_fragments = defaultdict(list)
    referenced_elias = defaultdict(list)

    for root, name in walk_repo(root_dir):
        ext = os.path.splitext(name)[1].lower()
        if ext not in TEXT_EXTS:
            continue

        abs_path = os.path.join(root, name)
        rel = relpath(abs_path, root_dir)

        text = safe_read(abs_path)
        if not text:
            continue

        for m in FRAG_REF_RE.finditer(text):
            n = int(m.group(1))
            referenced_fragments[n].append(rel)

        for m in ELIAS_REF_RE.finditer(text):
            n = int(m.group(1))
            referenced_elias[n].append(rel)

    frag_gaps = gaps(fragment_nums)
    elias_gaps = gaps(elias_nums)

    frag_missing = sorted([n for n in referenced_fragments.keys() if n not in fragment_paths])
    elias_missing = sorted([n for n in referenced_elias.keys() if n not in elias_paths])

    report = {
        "meta": {
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "type": "VOID_MAP",
            "policy": "REPORT_ONLY_NO_AUTOMATION"
        },
        "standard_fragments": {
            "count": len(set(fragment_nums)),
            "min": min(fragment_nums) if fragment_nums else None,
            "max": max(fragment_nums) if fragment_nums else None,
            "gap_count": len(frag_gaps),
            "missing_nodes": frag_gaps
        },
        "elias_placeholders": {
            "count": len(set(elias_nums)),
            "min": min(elias_nums) if elias_nums else None,
            "max": max(elias_nums) if elias_nums else None,
            "gap_count": len(elias_gaps),
            "missing_nodes": elias_gaps
        },
        "ghost_references": {
            "fragments_referenced_but_missing": [
                {"id": n, "referenced_in": sorted(set(referenced_fragments[n]))[:25]}
                for n in frag_missing
            ],
            "elias_referenced_but_missing": [
                {"id": n, "referenced_in": sorted(set(referenced_elias[n]))[:25]}
                for n in elias_missing
            ]
        }
    }

    json_path = os.path.join(OUT_DIR, "VOID_MAP_LATEST.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    md_path = os.path.join(OUT_DIR, "GHOST_ROOTS_MAP_LATEST.md")
    md = []
    md.append("# GHOST ROOTS MAP (Latest)")
    md.append(f"- Generated (UTC): {report['meta']['timestamp_utc']}")
    md.append("")
    md.append("## Standard Fragments")
    md.append(f"- Count: {report['standard_fragments']['count']}")
    md.append(f"- Range: {report['standard_fragments']['min']} -> {report['standard_fragments']['max']}")
    md.append(f"- Gaps: {report['standard_fragments']['gap_count']}")
    if report["standard_fragments"]["missing_nodes"]:
        md.append(f"- Missing: {', '.join(str(x) for x in report['standard_fragments']['missing_nodes'][:50])} ...")
    md.append("")
    md.append("## Elias Placeholders")
    md.append(f"- Count: {report['elias_placeholders']['count']}")
    md.append(f"- Range: {report['elias_placeholders']['min']} -> {report['elias_placeholders']['max']}")
    md.append(f"- Gaps: {report['elias_placeholders']['gap_count']}")
    if report["elias_placeholders"]["missing_nodes"]:
        md.append(f"- Missing: {', '.join(str(x) for x in report['elias_placeholders']['missing_nodes'][:50])} ...")
    md.append("")
    md.append("## Ghost References")
    md.append(f"- Missing Fragment IDs referenced somewhere: {len(report['ghost_references']['fragments_referenced_but_missing'])}")
    md.append(f"- Missing Elias IDs referenced somewhere: {len(report['ghost_references']['elias_referenced_but_missing'])}")
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"✅ Void Map written: {json_path}")

if __name__ == "__main__":
    main()
