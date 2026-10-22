#!/usr/bin/env python3
"""Build an exhaustive *advisory* Markdown classification inventory.

This is NOT a Law list: unknown remains unknown. Exact source headings are
evidence, not authority. The only approved section-level claim is explicitly
linked to the Keeper-directed 2026-10-22 ruling (not cryptographically signed).
"""
import argparse
import json
from pathlib import Path

try:
    from .full_corpus_envelopes import discover
except ImportError:
    from full_corpus_envelopes import discover

RULING = "tools/KEEPER_RULING_2026-10-22_SCROLL_SECTION_III.md"
SCROLL = "docs/Future_AI/CUSTODIANSHIP_SCROLL.md"


def build(root):
    root = Path(root).resolve()
    manifest = json.loads((root / "tools/retrieval_manifest.advisory.json").read_text(encoding="utf-8"))
    if manifest["status"] != "advisory_not_canon":
        raise ValueError("Refusing non-advisory manifest")
    reviewed = {entry["path"]: entry for entry in manifest["documents"]}
    paths = discover(root)
    if not set(reviewed).issubset(paths):
        raise ValueError("Reviewed manifest references missing sources")
    rows = []
    for path in paths:
        entry = reviewed.get(path)
        rows.append({
            "path": path,
            "classification": "advisory_reviewed" if entry else "unknown_pending_keeper_ruling",
            "document_status": entry.get("document_status", "unknown_pending_keeper_ruling") if entry else "unknown_pending_keeper_ruling",
            "law_authorized": False,
            "classification_source": "tools/retrieval_manifest.advisory.json" if entry else None
        })
    if SCROLL in paths:
        scroll = next(row for row in rows if row["path"] == SCROLL)
        if not (root / RULING).is_file():
            raise ValueError("Keeper ruling record missing")
        scroll["section_specific_claim"] = {
            "section": "III. The Veil and the Window",
            "ruling_record": RULING,
            "status": "keeper_directed_partial_ratification_not_independently_authenticated",
            "whole_document_law_authorized": False
        }
    return {"schema": "acacia.exhaustive-markdown-inventory/1",
            "status": "advisory_not_canon",
            "source": "checked_out_files",
            "count": len(rows),
            "reviewed_count": len(reviewed),
            "unknown_count": len(rows) - len(reviewed),
            "documents": rows}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--output")
    args = p.parse_args()
    result = json.dumps(build(args.root), indent=2, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
