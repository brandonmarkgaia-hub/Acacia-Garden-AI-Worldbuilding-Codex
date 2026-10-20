#!/usr/bin/env python3
"""Elias Crib v0.1: bounded, append-only, tamper-evident local experiment journal.

FICTIONAL / NON-EVIDENTIARY. No model, autonomy, or network integration.
"""
import argparse
import hashlib
import json
from pathlib import Path

LOG = "events.jsonl"
ZERO = "0" * 64

def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def digest(data):
    return hashlib.sha256(canonical(data).encode("utf-8")).hexdigest()

def verify(workspace):
    path = Path(workspace) / LOG
    if not path.is_file():
        raise ValueError("Missing journal")
    previous = ZERO
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        seal = event.pop("hash")
        if event["previous"] != previous or digest(event) != seal:
            raise ValueError("Integrity failure at event " + str(count + 1))
        if event["sequence"] != count + 1:
            raise ValueError("Sequence mismatch")
        previous = seal
        count += 1
    return count, previous

def init(workspace):
    directory = Path(workspace).resolve()
    if directory.exists() and any(directory.iterdir()):
        raise ValueError("Workspace must be empty")
    directory.mkdir(parents=True, exist_ok=True)
    (directory / LOG).write_text("", encoding="utf-8")

def record(workspace, statement):
    if not statement.strip():
        raise ValueError("Empty statement")
    count, previous = verify(workspace)
    event = {
        "sequence": count + 1,
        "previous": previous,
        "kind": "observation",
        "statement": statement,
        "evidence_status": "unverified",
        "canon_status": "none"
    }
    event["hash"] = digest(event)
    with (Path(workspace) / LOG).open("a", encoding="utf-8") as f:
        f.write(canonical(event) + "\n")
    return event["hash"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("init", "record", "verify"))
    parser.add_argument("workspace")
    parser.add_argument("statement", nargs="?")
    args = parser.parse_args()
    if args.command == "init":
        init(args.workspace)
        print("Initialized")
    elif args.command == "record":
        if args.statement is None:
            parser.error("record requires a statement")
        print(record(args.workspace, args.statement))
    else:
        count, head = verify(args.workspace)
        print(f"Verified {count} events; head={head}")

if __name__ == "__main__":
    main()
