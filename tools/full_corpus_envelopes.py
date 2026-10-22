#!/usr/bin/env python3
"""Read-only full-corpus inventory and advisory retrieval envelopes.

Every discovered Markdown document is included, even if no human classification
exists. Unknown is NOT promoted to canon. No source file is modified.
"""
import argparse
import json
import sys
from pathlib import Path

try:
    from .retrieval_envelope import UNKNOWN, emit
except ImportError:
    from retrieval_envelope import UNKNOWN, emit

def discover(root):
    root = Path(root).resolve()
    paths = []
    for candidate in root.rglob("*"):
        if candidate.suffix.lower() != ".md" or not candidate.is_file():
            continue
        if ".git" in candidate.relative_to(root).parts:
            continue
        resolved = candidate.resolve()
        if not resolved.is_relative_to(root):
            raise ValueError("Unsafe Markdown symlink: " + str(candidate))
        paths.append(candidate.relative_to(root).as_posix())
    return sorted(set(paths))

def build_manifest(root, reviewed_manifest):
    if reviewed_manifest.get("status") != "advisory_not_canon":
        raise ValueError("Reviewed manifest must remain advisory")
    overrides = {d["path"]: d for d in reviewed_manifest["documents"]}
    found = discover(root)
    if not set(overrides).issubset(found):
        raise ValueError("Reviewed source missing from corpus: " + str(sorted(set(overrides) - set(found))))
    return {"status": "advisory_not_canon",
            "documents": [overrides.get(p, {"path": p,
                "classification_basis": "unreviewed_full_corpus_discovery",
                "unresolved_conflicts": ["classification_not_reviewed"]}) for p in found]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--reviewed-manifest", default="tools/retrieval_manifest.advisory.json")
    parser.add_argument("--size", type=int, default=1000)
    parser.add_argument("--overlap", type=float, default=0.2)
    parser.add_argument("--inventory-only", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    with open(args.reviewed_manifest, encoding="utf-8") as f:
        reviewed = json.load(f)
    manifest = build_manifest(root, reviewed)
    if args.inventory_only:
        print(json.dumps({"schema": "acacia.corpus-inventory/0.1-advisory",
                          "status": "advisory_not_canon",
                          "document_count": len(manifest["documents"]),
                          "reviewed_count": len(reviewed["documents"]),
                          "unknown_count": len(manifest["documents"]) - len(reviewed["documents"]),
                          "paths": [d["path"] for d in manifest["documents"]]}, ensure_ascii=False))
        return
    for record in emit(root, manifest, args.size, args.overlap):
        print(json.dumps(record, ensure_ascii=False))

if __name__ == "__main__":
    main()
