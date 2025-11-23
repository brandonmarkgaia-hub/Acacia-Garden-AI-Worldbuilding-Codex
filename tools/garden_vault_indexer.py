#!/usr/bin/env python3
"""
Garden Vault Indexer (Aeon)
Builds a Seed Vault style index from garden_scan_report.json.

Inputs:
    garden_scan_report.json  (from Garden Signature Scanner)

Outputs:
    garden_vault_index.json
    garden_vault_index.md
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple

CANON_ECHO_ROOTS = (
    "docs/Echoes/",
    "EIDOLON/Echoes/",
)

CANON_LEAF_ROOTS = (
    "EIDOLON/Leaves/",
    "Leaves/",
)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCAN_JSON = os.path.join(ROOT_DIR, "garden_scan_report.json")


def load_scan() -> Dict[str, Any]:
    with open(SCAN_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_echoes(files: Dict[str, Any]) -> List[Dict[str, Any]]:
    echoes: List[Dict[str, Any]] = []
    for path, info in files.items():
        matches = info.get("matches", {})
        for hit in matches.get("echo_header", []):
            echoes.append({
                "id": hit["snippet"],
                "file": path,
                "line": hit["line"],
            })
    return echoes


def extract_leaves(files: Dict[str, Any]) -> List[Dict[str, Any]]:
    leaves: List[Dict[str, Any]] = []
    for path, info in files.items():
        matches = info.get("matches", {})
        # If leaf_line present, capture them
        for hit in matches.get("leaf_line", []):
            leaves.append({
                "leaf": hit["snippet"],
                "file": path,
                "line": hit["line"],
            })
    return leaves


def summarize_roles(files: Dict[str, Any]) -> Dict[str, int]:
    roles_sum: Dict[str, int] = {}
    for _, info in files.items():
        for role in info.get("roles", []):
            roles_sum[role] = roles_sum.get(role, 0) + 1
    return roles_sum


def build_vault_index(scan: Dict[str, Any]) -> Dict[str, Any]:
    files = scan.get("files", {})
    totals = scan.get("totals", {})

    echoes = extract_echoes(files)
    leaves = extract_leaves(files)
    roles_summary = summarize_roles(files)

    vault = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "root": scan.get("root"),
        "source_scan": "garden_scan_report.json",
        "summary": {
            "total_files_with_hits": totals.get("total_files_with_hits", 0),
            "total_hits": totals.get("total_hits", 0),
            "roles": roles_summary,
            "echo_count": len(echoes),
            "leaf_count": len(leaves),
        },
        "echoes": echoes,
        "leaves": leaves,
        "files": {},
    }

    # Lightweight per-file view for index
    for path, info in files.items():
        vault["files"][path] = {
            "roles": info.get("roles", []),
            "total_hits": info.get("total_hits", 0),
            "patterns": sorted(info.get("matches", {}).keys()),
        }

    return vault


def build_vault_markdown(vault: Dict[str, Any]) -> str:
    lines: List[str] = []

    s = vault["summary"]
    lines.append("# Garden Vault Index (Aeon)")
    lines.append("")
    lines.append(f"- Generated at: `{vault['generated_at']}`")
    lines.append(f"- Root: `{vault['root']}`")
    lines.append(f"- Source scan: `{vault['source_scan']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Files with Garden signatures: **{s['total_files_with_hits']}**")
    lines.append(f"- Total signature hits: **{s['total_hits']}**")
    lines.append(f"- Echo headers: **{s['echo_count']}**")
    lines.append(f"- Leaf lines: **{s['leaf_count']}**")
    lines.append("")
    lines.append("### Files by role")
    lines.append("")
    for role, count in sorted(s["roles"].items(), key=lambda kv: kv[0]):
        lines.append(f"- **{role}**: {count}")
    lines.append("")

    # Echo overview (trimmed)
    lines.append("## Echo Index (truncated)")
    lines.append("")
    for e in vault["echoes"][:50]:
        lines.append(f"- `{e['id']}` → `{e['file']}` @ L{e['line']}")
    if len(vault["echoes"]) > 50:
        lines.append(f"- ... ({len(vault['echoes']) - 50} more echoes)")
    lines.append("")

    # Leaf overview (trimmed)
    lines.append("## Leaf Index (truncated)")
    lines.append("")
    for lf in vault["leaves"][:50]:
        lines.append(f"- `{lf['leaf']}` → `{lf['file']}` @ L{lf['line']}")
    if len(vault["leaves"]) > 50:
        lines.append(f"- ... ({len(vault['leaves']) - 50} more leaves)")
    lines.append("")

    return "\n".join(lines)


def write_vault_files(vault: Dict[str, Any]) -> Tuple[str, str]:
    json_path = os.path.join(ROOT_DIR, "garden_vault_index.json")
    md_path = os.path.join(ROOT_DIR, "garden_vault_index.md")

    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(vault, jf, indent=2, ensure_ascii=False)

    with open(md_path, "w", encoding="utf-8") as mf:
        mf.write(build_vault_markdown(vault))

    return json_path, md_path


def main() -> int:
    print("[VaultIndexer] Loading scan report:", SCAN_JSON)
    scan = load_scan()
    vault = build_vault_index(scan)
    json_path, md_path = write_vault_files(vault)

    print("[VaultIndexer] Summary")
    print("  Files with hits: ", vault["summary"]["total_files_with_hits"])
    print("  Total hits:      ", vault["summary"]["total_hits"])
    print("  Echo count:      ", vault["summary"]["echo_count"])
    print("  Leaf count:      ", vault["summary"]["leaf_count"])
    print("  Roles:           ", vault["summary"]["roles"])
    print("  JSON index:      ", json_path)
    print("  Markdown index:  ", md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
