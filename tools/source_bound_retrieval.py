#!/usr/bin/env python3
"""Source-bound retrieval audit. Validate envelopes against checked-out files.

Integrity is relative to the chosen checkout, NOT proof of authorship, Keeper
approval, or canonical authority. The checkout's provenance is an external
trust decision. Never follow an envelope's claim about its own authority.
"""
import argparse
import json
from pathlib import Path

try:
    from .retrieval_envelope import digest, verify_record
    from .retrieval_safety_gate import assess
    from .retrieval_context_boundary import derive_context
except ImportError:
    from retrieval_envelope import digest, verify_record
    from retrieval_safety_gate import assess
    from retrieval_context_boundary import derive_context

def validate_envelope_shape(record):
    """Reject malformed untrusted metadata before touching the checkout."""
    required_strings = ("source_path", "source_sha256", "chunk_sha256", "text",
                        "document_status", "voice_class", "authority_scope",
                        "authorship_status", "authorization_status",
                        "keeper_approval", "canonical_effect", "metadata_trust")
    if not isinstance(record, dict):
        return False
    if any(not isinstance(record.get(key), str) for key in required_strings):
        return False
    if any(not isinstance(record.get(key), int) or isinstance(record.get(key), bool)
           for key in ("start_offset", "end_offset")):
        return False
    if record["start_offset"] < 0 or record["end_offset"] <= record["start_offset"]:
        return False
    if not isinstance(record.get("unresolved_conflicts"), list):
        return False
    if any(not isinstance(x, str) for x in record["unresolved_conflicts"]):
        return False
    if any(not isinstance(record.get(k), str) or len(record[k]) != 64
           or any(c not in "0123456789abcdef" for c in record[k])
           for k in ("source_sha256", "chunk_sha256")):
        return False
    return True


def verify_against_checkout(root, record):
    if not validate_envelope_shape(record):
        return False, "invalid_envelope_schema"
    rel = record.get("source_path")
    if not isinstance(rel, str) or not rel or "\\" in rel:
        return False, "invalid_source_path"
    root = Path(root).resolve()
    relative = Path(rel)
    if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != rel:
        return False, "invalid_source_path"
    source = (root / relative).resolve()
    if not source.is_relative_to(root) or not source.is_file():
        return False, "unsafe_or_missing_source"
    try:
        text = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False, "unreadable_source"
    # The hash is independently recomputed from the selected checkout, rather
    # than trusting the value supplied in the retrieved record.
    if not verify_record(record, text, digest(text)):
        return False, "source_or_window_integrity_failure"
    return True, "checkout_integrity_verified_not_authenticated"

def assess_bound(root, record):
    ok, reason = verify_against_checkout(root, record)
    if not ok:
        return {"decision": "reject", "reasons": [reason], "actionable": False,
                "canon_authorized": False}
    context = derive_context(root, record)
    if context is None:
        return {"decision": "reject", "reasons": ["source_context_boundary_unverifiable"],
                "actionable": False, "canon_authorized": False}
    outcome = assess(record)
    if outcome["decision"] == "reject":
        return outcome
    # Never promote untrusted advisory status into quotation permission.
    outcome = {**outcome, "decision": "context_only",
               "reasons": outcome.get("reasons", []) + ["source_context_required"]}
    return {**outcome, "source_context": context,
            "source_integrity": "verified_against_checkout",
            "source_authenticity": "not_authenticated",
            "keeper_approval": "not_established"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if Path(args.input).resolve() == Path(args.output).resolve():
        parser.error("Output must not overwrite input")
    root = Path(args.root).resolve()
    with open(args.input, encoding="utf-8") as src, open(args.output, "w", encoding="utf-8") as dest:
        for line in src:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                record = None
            dest.write(json.dumps(assess_bound(root, record), ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
