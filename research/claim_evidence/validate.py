#!/usr/bin/env python3
"""Fail-closed structural validator for experimental CEV records."""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
ALLOWED = {"AUTHORITY.json", "AGENTS.md", "DISCOVERY.md", "STATUS.json", "llms.txt"}
KINDS = {"observed_text", "inference", "proposal", "historical_narrative"}
STATUSES = {"unverified", "evidence_checked", "independently_verified"}


def validate(data, root=ROOT):
    errors = []
    if not isinstance(data, dict) or data.get("schema") != "acacia.cev/0.1" or not isinstance(data.get("records"), list):
        return ["Invalid CEV envelope"]
    seen = set()
    for i, record in enumerate(data["records"]):
        tag = f"records[{i}]"
        if not isinstance(record, dict):
            errors.append(f"{tag}: not an object")
            continue
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            errors.append(f"{tag}: missing or duplicate id")
        else:
            seen.add(identifier)
        if not isinstance(record.get("claim"), str) or not record["claim"].strip():
            errors.append(f"{tag}: missing claim")
        kind = record.get("claim_type")
        status = record.get("verification")
        if kind not in KINDS:
            errors.append(f"{tag}: invalid claim_type")
        if status not in STATUSES:
            errors.append(f"{tag}: invalid verification")
        evidence = record.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{tag}: evidence must be a list")
            continue
        if status != "unverified" and not evidence:
            errors.append(f"{tag}: verified status requires evidence")
        if kind in {"proposal", "historical_narrative"} and status != "unverified":
            errors.append(f"{tag}: proposal/narrative cannot be verified as operational fact")
        for j, item in enumerate(evidence):
            prefix = f"{tag}.evidence[{j}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix}: not an object")
                continue
            path = item.get("path")
            if not isinstance(path, str) or path not in ALLOWED:
                errors.append(f"{prefix}: path not allowlisted")
                continue
            file = root / path
            if file.is_symlink() or not file.is_file():
                errors.append(f"{prefix}: missing or symlink source")
                continue
            content = file.read_bytes()
            excerpt = item.get("excerpt")
            if not isinstance(excerpt, str) or not excerpt or excerpt.encode("utf-8") not in content:
                errors.append(f"{prefix}: excerpt absent")
            digest = item.get("sha256")
            if digest is not None and digest != hashlib.sha256(content).hexdigest():
                errors.append(f"{prefix}: sha256 mismatch")
    return errors


def main():
    if len(sys.argv) != 2:
        print("usage: validate.py RECORDS.json", file=sys.stderr)
        return 2
    try:
        data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    for error in errors:
        print(error, file=sys.stderr)
    print(f"CEV records: {len(data.get('records', [])) if isinstance(data, dict) else 0}; errors: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
