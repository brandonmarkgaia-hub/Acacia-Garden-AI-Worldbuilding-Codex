#!/usr/bin/env python3
"""Fail-closed structural validator for experimental CEV records."""
import hashlib
import json
import pathlib
import sys
import os
import stat

ROOT = pathlib.Path(__file__).resolve().parents[2]
ALLOWED = {"AUTHORITY.json", "AGENTS.md", "DISCOVERY.md", "STATUS.json", "llms.txt"}
KINDS = {"observed_text", "inference", "proposal", "historical_narrative"}
STATUSES = {"unverified", "evidence_checked", "independently_verified"}


def validate(data, root=ROOT):
    errors = []
    if not isinstance(data, dict) or data.get("schema") != "acacia.cev/0.1" or not isinstance(data.get("records"), list):
        return ["Invalid CEV envelope"]
    seen = set()
    allowed_record_keys = {"id", "claim", "claim_type", "verification", "evidence", "limitations"}
    allowed_evidence_keys = {"path", "excerpt", "sha256"}
    for i, record in enumerate(data["records"]):
        tag = f"records[{i}]"
        if not isinstance(record, dict):
            errors.append(f"{tag}: not an object")
            continue
        for key in record.keys() - allowed_record_keys:
            errors.append(f"{tag}: unknown record field {key!r}")
        limitations = record.get("limitations", [])
        if not isinstance(limitations, list) or any(not isinstance(value, str) or not value.strip() for value in limitations):
            errors.append(f"{tag}: limitations must be a list of nonempty strings")
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            errors.append(f"{tag}: missing or duplicate id")
        else:
            seen.add(identifier)
        if not isinstance(record.get("claim"), str) or not record["claim"].strip():
            errors.append(f"{tag}: missing claim")
        kind = record.get("claim_type")
        status = record.get("verification")
        if not isinstance(kind, str) or kind not in KINDS:
            errors.append(f"{tag}: invalid claim_type")
        if not isinstance(status, str) or status not in STATUSES:
            errors.append(f"{tag}: invalid verification")
        if status == "independently_verified":
            errors.append(f"{tag}: independent verification unsupported without external review protocol")
        evidence = record.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{tag}: evidence must be a list")
            continue
        if status != "unverified" and not evidence:
            errors.append(f"{tag}: verified status requires evidence")
        if isinstance(kind, str) and kind in {"proposal", "historical_narrative"} and status != "unverified":
            errors.append(f"{tag}: proposal/narrative cannot be verified as operational fact")
        for j, item in enumerate(evidence):
            prefix = f"{tag}.evidence[{j}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix}: not an object")
                continue
            for key in item.keys() - allowed_evidence_keys:
                errors.append(f"{prefix}: unknown evidence field {key!r}")
            path = item.get("path")
            if not isinstance(path, str) or path not in ALLOWED:
                errors.append(f"{prefix}: path not allowlisted")
                continue
            file = root / path
            try:
                if file.is_symlink() or not file.is_file():
                    errors.append(f"{prefix}: missing or symlink source")
                    continue
                metadata = file.stat(follow_symlinks=False)
                if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                    errors.append(f"{prefix}: source is not a single-link regular file")
                    continue
                content = file.read_bytes()
            except OSError as exc:
                errors.append(f"{prefix}: unreadable source ({type(exc).__name__})")
                continue
            excerpt = item.get("excerpt")
            try:
                needle = excerpt.encode("utf-8") if isinstance(excerpt, str) else b""
            except UnicodeEncodeError:
                needle = b""
            if not needle or not needle.strip() or needle not in content:
                errors.append(f"{prefix}: excerpt absent")
            digest = item.get("sha256")
            if digest is not None and (not isinstance(digest, str) or digest != hashlib.sha256(content).hexdigest()):
                errors.append(f"{prefix}: sha256 mismatch")
    return errors


def main():
    if len(sys.argv) != 2:
        print("usage: validate.py RECORDS.json", file=sys.stderr)
        return 2
    try:
        def reject_duplicate_keys(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f"Duplicate JSON key: {key}")
                result[key] = value
            return result

        def reject_nonfinite(value):
            raise ValueError(f"Non-finite JSON number: {value}")

        data = json.loads(
            pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_nonfinite,
        )
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    try:
        errors = validate(data)
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError, OverflowError) as exc:
        print(f"Validation error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    for error in errors:
        print(error, file=sys.stderr)
    records = data.get("records") if isinstance(data, dict) else None
    print(f"CEV records: {len(records) if isinstance(records, list) else 0}; errors: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
