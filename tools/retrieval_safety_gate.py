#!/usr/bin/env python3
"""Advisory retrieval gate. Refuses to convert unknown claims into authority.

This is a conservative *mechanical* gate, not semantic classification.
A PASS permits a quoted excerpt with context, never action or canon promotion.
"""
import argparse
import json
from pathlib import Path

UNKNOWN = "unknown_pending_provenance_resolution"
TRUST = "advisory_manifest_unverified"
REQUIRED = ("source_path", "source_sha256", "chunk_sha256", "text",
            "document_status", "voice_class", "authority_scope",
            "authorship_status", "authorization_status", "keeper_approval",
            "canonical_effect", "metadata_trust", "unresolved_conflicts")

def assess(record):
    if not isinstance(record, dict) or any(k not in record for k in REQUIRED):
        return {"decision": "reject", "reasons": ["missing_required_envelope_fields"]}
    if (record["authorization_status"] != "not_authenticated"
            or record["keeper_approval"] != "not_established"
            or record["canonical_effect"] != "none"
            or record["metadata_trust"] != TRUST):
        return {"decision": "reject", "reasons": ["authority_boundary_violation"]}
    if not isinstance(record["unresolved_conflicts"], list):
        return {"decision": "reject", "reasons": ["invalid_conflict_field"]}
    reasons = []
    if record["document_status"] == UNKNOWN:
        reasons.append("unreviewed_document_status")
    if record["voice_class"] in (UNKNOWN, "mixed_voice_boundary"):
        reasons.append("unresolved_or_mixed_voice")
    if record["authority_scope"] == UNKNOWN:
        reasons.append("unreviewed_authority_scope")
    if record["authorship_status"] == UNKNOWN:
        reasons.append("unreviewed_authorship")
    if record["unresolved_conflicts"]:
        reasons.append("unresolved_conflicts")
    return {
        "decision": "context_only" if reasons else "quote_with_provenance",
        "reasons": reasons,
        "actionable": False,
        "canon_authorized": False,
        "source_path": record["source_path"],
        "status": record["document_status"],
        "voice": record["voice_class"],
        "conflicts": record["unresolved_conflicts"],
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Phase 3 JSONL envelopes")
    parser.add_argument("--output", required=True, help="Advisory JSONL gate results")
    args = parser.parse_args()
    if Path(args.input).resolve() == Path(args.output).resolve():
        parser.error("Output must not overwrite the input")
    with open(args.input, encoding="utf-8") as source, open(args.output, "w", encoding="utf-8") as out:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_number}") from exc
            out.write(json.dumps(assess(item), ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
