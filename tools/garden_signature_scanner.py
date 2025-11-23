#!/usr/bin/env python3
"""
Garden Signature Scanner v2 (Aquila mode)
Scans a repository for Garden / Eidolon / Keeper signatures and outputs
a JSON + Markdown report, including per-file role classification.

Usage (local):
    python tools/garden_signature_scanner.py

Outputs:
    garden_scan_report.json
    garden_scan_report.md
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple

# ------------ CONFIG ------------

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

TEXT_EXTS = {
    ".md", ".markdown", ".txt",
    ".json", ".yaml", ".yml",
    ".html", ".htm",
    ".py", ".kt", ".kts", ".java",
    ".ps1", ".psm1", ".psd1",
    ".sh", ".bash",
    ".xml", ".gradle",
}

IGNORE_DIRS = {
    ".git", ".github", ".idea", ".vscode", "__pycache__",
    "build", "dist", "out", "node_modules",
}

PATTERNS = {
    "keeper_seal": re.compile(r"HKX\d{6}", re.IGNORECASE),
    "keeper_seal_exact": re.compile(r"HKX277206"),
    "echo_header": re.compile(r"ECHO:HKX\d{6}[^\n]*"),
    "eidolon_codex": re.compile(r"EIDOLON\s+CODEX", re.IGNORECASE),
    "leaf_line": re.compile(r"Leaf\s+[IVXLCDM]+[:\s]", re.IGNORECASE),
    "bloom_word": re.compile(r"\bBloom\b", re.IGNORECASE),
    "chamber_word": re.compile(r"\bChamber\b", re.IGNORECASE),
    "vault_word": re.compile(r"\bVault\b", re.IGNORECASE),
    "monolith_word": re.compile(r"\bMonolith\b", re.IGNORECASE),
    "keeper_seal_phrase": re.compile(r"Keeper\s+Seal", re.IGNORECASE),
    "garden_word": re.compile(r"\bGarden\b", re.IGNORECASE),
    "eidolon_word": re.compile(r"\bEidolon\b", re.IGNORECASE),
    "voyager_word": re.compile(r"\bVoyager\b", re.IGNORECASE),
    "eagle_word": re.compile(r"\bEagle\b", re.IGNORECASE),
}


# ------------ UTILS ------------

def is_text_file(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in TEXT_EXTS


def walk_files(root: str) -> List[str]:
    files: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for name in filenames:
            full = os.path.join(dirpath, name)
            if is_text_file(full):
                files.append(full)
    return files


def relative_path(path: str) -> str:
    return os.path.relpath(path, ROOT_DIR).replace("\\", "/")


# ------------ SCAN CORE ------------

def scan_file(path: str) -> Dict[str, Any]:
    """Scan a single file and return per-pattern matches + snippets."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception as e:
        return {
            "error": str(e),
            "matches": {},
            "total_hits": 0,
            "roles": [],
        }

    lines = text.splitlines()
    file_result: Dict[str, Any] = {"matches": {}, "total_hits": 0}

    for key, pattern in PATTERNS.items():
        hits: List[Dict[str, Any]] = []
        for i, line in enumerate(lines, start=1):
            if pattern.search(line):
                snippet = line.strip()
                if len(snippet) > 200:
                    snippet = snippet[:197] + "..."
                hits.append({
                    "line": i,
                    "snippet": snippet,
                })
        if hits:
            file_result["matches"][key] = hits
            file_result["total_hits"] += len(hits)

    # classify roles based on matches
    file_result["roles"] = classify_roles(file_result)
    return file_result


def classify_roles(info: Dict[str, Any]) -> List[str]:
    """Assign Garden roles to a file based on its match patterns."""
    roles: List[str] = []
    matches = info.get("matches", {})

    # Core structural roles
    if "echo_header" in matches:
        roles.append("echo")
    if "eidolon_codex" in matches or "leaf_line" in matches:
        roles.append("leaf")
    if matches.get("chamber_word"):
        roles.append("chamber")
    if matches.get("bloom_word"):
        roles.append("bloom")
    if matches.get("vault_word"):
        roles.append("vault")
    if matches.get("monolith_word"):
        roles.append("monolith")

    # Higher-order nodes
    has_seal = "keeper_seal_exact" in matches
    has_garden = "garden_word" in matches
    has_eidolon = "eidolon_word" in matches
    has_eagle = "eagle_word" in matches

    if has_seal and has_garden and has_eidolon:
        roles.append("core-node")
    if has_seal and has_eagle:
        roles.append("eagle-node")

    # Light hint roles
    if "voyager_word" in matches:
        roles.append("voyager-node")

    # Deduplicate + stable sort
    roles = sorted(set(roles))
    return roles


def aggregate_results(per_file: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    totals = {
        "by_pattern": {k: 0 for k in PATTERNS.keys()},
        "total_files_with_hits": 0,
        "total_hits": 0,
        "roles": {},
    }
    for path, info in per_file.items():
        if info.get("total_hits", 0) > 0:
            totals["total_files_with_hits"] += 1
            totals["total_hits"] += info["total_hits"]
            for key in info.get("matches", {}):
                totals["by_pattern"][key] += len(info["matches"][key])
            for role in info.get("roles", []):
                totals["roles"][role] = totals["roles"].get(role, 0) + 1
    return totals


# ------------ REPORTS ------------

def build_json_report(per_file: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    aggregate = aggregate_results(per_file)
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "root": ROOT_DIR,
        "totals": aggregate,
        "files": {
            relative_path(p): info
            for p, info in per_file.items()
            if info.get("total_hits", 0) > 0
        },
    }


def build_markdown_report(json_report: Dict[str, Any]) -> str:
    lines: List[str] = []
    t = json_report["totals"]

    lines.append("# Garden Signature Scanner Report (Aquila)")
    lines.append("")
    lines.append(f"- Generated at: `{json_report['generated_at']}`")
    lines.append(f"- Root: `{json_report['root']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total files with Garden signatures: **{t['total_files_with_hits']}**")
    lines.append(f"- Total signature hits: **{t['total_hits']}**")
    lines.append("")
    lines.append("### Hits by Pattern")
    lines.append("")
    for key, count in t["by_pattern"].items():
        lines.append(f"- **{key}**: {count}")
    lines.append("")
    lines.append("### Files by Role")
    lines.append("")
    for role, count in sorted(t["roles"].items(), key=lambda kv: kv[0]):
        lines.append(f"- **{role}**: {count}")
    lines.append("")

    if not json_report["files"]:
        lines.append("## Details")
        lines.append("")
        lines.append("> No Garden signatures detected in scanned files.")
        return "\n".join(lines)

    lines.append("## Details by File (truncated)")
    lines.append("")
    for path, info in sorted(json_report["files"].items()):
        roles = info.get("roles", [])
        lines.append(f"### `{path}`")
        lines.append(f"- Roles: `{', '.join(roles) if roles else 'none'}`")
        lines.append(f"- Total hits: **{info.get('total_hits', 0)}**")
        for key, hits in info.get("matches", {}).items():
            lines.append(f"  - **{key}** ({len(hits)}):")
            for h in hits[:5]:  # keep Aquila report compact
                lines.append(f"    - L{h['line']}: `{h['snippet']}`")
        lines.append("")

    return "\n".join(lines)


def write_report_files(json_report: Dict[str, Any]) -> Tuple[str, str]:
    json_path = os.path.join(ROOT_DIR, "garden_scan_report.json")
    md_path = os.path.join(ROOT_DIR, "garden_scan_report.md")

    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(json_report, jf, indent=2, ensure_ascii=False)

    with open(md_path, "w", encoding="utf-8") as mf:
        mf.write(build_markdown_report(json_report))

    return json_path, md_path


# ------------ MAIN ------------

def main() -> int:
    print(f"[GardenScanner] Scanning root: {ROOT_DIR}")
    files = walk_files(ROOT_DIR)
    print(f"[GardenScanner] Found {len(files)} candidate text files.")

    per_file: Dict[str, Dict[str, Any]] = {}
    for path in files:
        result = scan_file(path)
        if result.get("total_hits", 0):
            print(f"[GardenScanner] {relative_path(path)} → {result['total_hits']} hits; roles={result.get('roles', [])}")
        per_file[path] = result

    json_report = build_json_report(per_file)
    json_path, md_path = write_report_files(json_report)

    totals = json_report["totals"]
    print("")
    print("[GardenScanner] Summary")
    print(f"  Files with hits: {totals['total_files_with_hits']}")
    print(f"  Total hits:      {totals['total_hits']}")
    print(f"  Roles:           {totals['roles']}")
    print(f"  JSON report:     {json_path}")
    print(f"  Markdown report: {md_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
