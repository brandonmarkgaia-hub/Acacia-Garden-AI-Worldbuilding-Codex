#!/usr/bin/env python3
"""Generate review-only cross-document conflict candidates with exact source anchors.

Only explicit reviewer-supplied anchors qualify. This is NOT automated semantic
contradiction detection and never decides truth, precedence or canon.
"""
import argparse
import hashlib
import json
from pathlib import Path

def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def locate(root, item):
    rel = item["path"]
    root = Path(root).resolve()
    source = (root / rel).resolve()
    if not source.is_relative_to(root) or not source.is_file():
        raise ValueError("Unsafe or missing evidence source: " + rel)
    text = source.read_text(encoding="utf-8")
    anchor = item["exact_anchor"]
    if not isinstance(anchor, str) or not anchor.strip():
        raise ValueError("Empty evidence anchor")
    if text.count(anchor) != 1:
        raise ValueError("Evidence anchor must occur exactly once: " + rel)
    start = text.index(anchor)
    return {"path": rel, "start_offset": start, "end_offset": start + len(anchor),
            "exact_anchor": anchor, "source_sha256": sha(text),
            "anchor_sha256": sha(anchor)}

def review_candidates(root, spec):
    if spec.get("status") != "advisory_not_canon":
        raise ValueError("Conflict specification must remain advisory")
    for candidate in spec["candidates"]:
        evidence = candidate["evidence"]
        if len(evidence) < 2 or len({e["path"] for e in evidence}) < 2:
            raise ValueError("Cross-document conflict needs at least two different sources")
        yield {"schema": "acacia.conflict-candidate/0.1-advisory",
               "id": candidate["id"],
               "hypothesis": candidate["hypothesis"],
               "evidence": [locate(root, item) for item in evidence],
               "decision": "human_review_required",
               "truth_decided": False, "canon_authorized": False,
               "keeper_approval": "not_established",
               "metadata_trust": "advisory_manifest_unverified"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--spec", required=True)
    args = parser.parse_args()
    with open(args.spec, encoding="utf-8") as handle:
        spec = json.load(handle)
    for record in review_candidates(args.root, spec):
        print(json.dumps(record, ensure_ascii=False))

if __name__ == "__main__":
    main()
