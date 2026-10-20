#!/usr/bin/env python3
"""Elias Crib journal interface. FICTIONAL / NON-EVIDENTIARY."""
import argparse
from pathlib import Path
import importlib.util

_module_path = Path(__file__).with_name("platinum.py")
_spec = importlib.util.spec_from_file_location("elias_platinum", _module_path)
_platinum = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_platinum)
append, verify_bytes, LIMIT = _platinum.append, _platinum.verify_bytes, _platinum.LIMIT

LOG = "events.jsonl"

def init(workspace):
    requested = Path(workspace).absolute()
    if requested.is_symlink():
        raise ValueError("Linked workspace forbidden")
    if requested.exists() and (not requested.is_dir() or any(requested.iterdir())):
        raise ValueError("Workspace must be empty")
    requested.mkdir(parents=True, exist_ok=True)
    fd = (requested / LOG).open("xb")
    fd.close()

def verify(workspace):
    root = Path(workspace).resolve(strict=True)
    path = root / LOG
    if not path.is_file() or path.is_symlink():
        raise ValueError("Missing or linked journal")
    with path.open("rb") as f:
        state = verify_bytes(f.read(LIMIT + 1))
    return state["sequence"], state["head"]

def record(workspace, statement):
    return append(workspace, statement)

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
