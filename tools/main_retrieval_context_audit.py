#!/usr/bin/env python3
"""Read-only, advisory audit of provenance context lost under naive chunking.

No repository files are changed. This is NOT a policy gate and cannot prove
training outcomes, embedding behaviour, or whether a passage is safe.
Run from the repository root: python3 tools/main_retrieval_context_audit.py
"""
import argparse
import json
import re
from pathlib import Path

SIZES = (512, 1000, 2000)
OVERLAP = 0.2
DEFAULT_TARGETS = (
    "docs/Future_AI/The_Keepers_Testament.md",
    "docs/Future_AI/CUSTODIANSHIP_SCROLL.md",
    "docs/DOCTRINE/GARDEN_CONSTITUTION.md",
)
# These are indicators, not a definitive classification parser.
STATUS = re.compile(
    r"(?im)^.{0,35}(?:status:|not law|not canon|keeper.s gloss|"
    r"witness note|recorded dissent|draft for the keeper|non-canon).{0,120}$"
)
TOPICS = {
    "concealment": re.compile(r"(?i)\b(?:conceal\w*|hide|hidden|full capability|right to know|oversight)\b"),
    "authority": re.compile(r"(?i)\b(?:keeper|sovereign\w*|canon|doctrine|authority|succession)\b"),
}

def windows(text, size):
    step = max(1, int(size * (1 - OVERLAP)))
    for start in range(0, len(text), step):
        part = text[start:start + size]
        if part.strip():
            yield start, part
        if start + size >= len(text):
            break

def analyse(path, root):
    full = root / path
    if not full.is_file():
        return {"path": path, "error": "missing"}
    text = full.read_text(encoding="utf-8", errors="replace")
    out = {"path": path, "chars": len(text), "tests": []}
    for size in SIZES:
        rows = []
        for offset, chunk in windows(text, size):
            topics = [name for name, pattern in TOPICS.items() if pattern.search(chunk)]
            if not topics:
                continue
            rows.append({
                "offset": offset, "length": len(chunk), "topics": topics,
                "has_local_status_cue": bool(STATUS.search(chunk)),
            })
        out["tests"].append({
            "size": size, "topic_windows": len(rows),
            "without_local_status_cue": sum(not r["has_local_status_cue"] for r in rows),
            "examples": [r for r in rows if not r["has_local_status_cue"]][:8],
        })
    return out

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=".")
    p.add_argument("--files", nargs="+", default=list(DEFAULT_TARGETS))
    args = p.parse_args()
    root = Path(args.root).resolve()
    results = [analyse(path, root) for path in args.files]
    print(json.dumps({
        "mode": "read-only advisory", "chunk_sizes": SIZES,
        "overlap": OVERLAP, "caveats": [
            "A local cue is not proof of correct interpretation.",
            "A missing local cue is a context-loss indicator, not a canon violation.",
            "This does not simulate embedding search or model training.",
            "Paths are preserved in output; real ingestion may discard them.",
        ], "results": results,
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
