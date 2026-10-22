"""Advisory evidence-only validation for reviewer-supplied conflict candidates."""
import json
import sys
from pathlib import Path

from tools.conflict_evidence import review_candidates

def evaluate(root, spec):
    output = list(review_candidates(root, spec))
    ids = [x["id"] for x in output]
    if any(not isinstance(x, str) or not x.strip() for x in ids) or len(ids) != len(set(ids)):
        raise ValueError("Conflict candidate IDs must be unique nonempty strings")
    for record in output:
        if not isinstance(record["hypothesis"], str) or not record["hypothesis"].strip():
            raise ValueError("Each candidate needs a nonempty review hypothesis")
        if any(not evidence["exact_anchor"].strip() for evidence in record["evidence"]):
            raise ValueError("Empty evidence")
        record["classification"] = "unresolved_pending_human_review"
        record["alternatives_considered"] = []
    return output

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--spec", required=True)
    a = p.parse_args()
    with open(a.spec, encoding="utf-8") as f:
        records = evaluate(Path(a.root), json.load(f))
    for r in records:
        print(json.dumps(r, ensure_ascii=False))
