#!/usr/bin/env python3
"""Bounded local Crib journal operations. FICTIONAL / NON-EVIDENTIARY."""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path

ZERO = "0" * 64
LIMIT = 10 * 1024 * 1024

def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha(x):
    return hashlib.sha256(x).hexdigest()

def verify_bytes(data):
    if len(data) > LIMIT or (data and not data.endswith(b"\n")):
        raise ValueError("Oversized or incomplete journal")
    head, count = ZERO, 0
    for line in data.splitlines():
        event = json.loads(line)
        if not isinstance(event, dict) or "hash" not in event:
            raise ValueError("Malformed event")
        claimed = event.pop("hash")
        count += 1
        if event.get("sequence") != count or event.get("previous") != head or sha(canonical(event).encode()) != claimed:
            raise ValueError("Journal chain mismatch")
        head = claimed
    return {"sequence": count, "head": head, "sha256": sha(data)}

@contextlib.contextmanager
def locked(workspace):
    root = Path(workspace).resolve(strict=True)
    journal = root / "events.jsonl"
    lock = root / ".crib.lock"
    if not root.is_dir() or not journal.is_file() or journal.is_symlink() or lock.is_symlink():
        raise ValueError("Invalid workspace")
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield root, journal
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)

def append(workspace, note, kind="observation"):
    if kind not in ("observation", "hypothesis", "revision") or not isinstance(note, str) or not note.strip() or len(note.encode()) > 4096:
        raise ValueError("Invalid entry")
    with locked(workspace) as (_, journal):
        with journal.open("r+b") as f:
            data = f.read(LIMIT + 1)
            state = verify_bytes(data)
            event = {"sequence": state["sequence"] + 1, "previous": state["head"], "kind": kind, "statement": note, "evidence_status": "unverified", "canon_status": "none"}
            event["hash"] = sha(canonical(event).encode())
            payload = (canonical(event) + "\n").encode()
            if len(data) + len(payload) > LIMIT:
                raise ValueError("Journal full")
            f.seek(0, os.SEEK_END)
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
            return event["hash"]

def anchor(workspace, destination):
    target = Path(destination).absolute()
    if target.exists():
        raise ValueError("Anchor exists")
    with locked(workspace) as (root, journal):
        if root == target or root in target.parents:
            raise ValueError("Anchor must be external")
        state = verify_bytes(journal.read_bytes())
        fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write((canonical(state) + "\n").encode())
            f.flush()
            os.fsync(f.fileno())
    return state

def check_anchor(workspace, destination):
    target = Path(destination)
    if target.is_symlink():
        raise ValueError("Linked anchor")
    expected = json.loads(target.read_text())
    with locked(workspace) as (_, journal):
        actual = verify_bytes(journal.read_bytes())
    if expected != actual:
        raise ValueError("Anchor mismatch")
    return actual

def reflect(question, source):
    """Deterministic evidence checklist; no external model or tool actions."""
    if not isinstance(question, str) or not 0 < len(question) <= 500 or not isinstance(source, dict) or not isinstance(source.get("source"), str) or not isinstance(source.get("sha256"), str) or len(source["sha256"]) != 64:
        raise ValueError("Question and source citation required")
    return {"question": question, "source": source["source"], "sha256": source["sha256"], "evidence_status": "unverified", "canon_status": "none", "questions_to_check": ["What does the source actually support?", "What alternative explanation fits?", "What would disconfirm this interpretation?"], "automated_actions": 0}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("append", "anchor", "check-anchor"))
    parser.add_argument("workspace")
    parser.add_argument("argument")
    parser.add_argument("--kind", default="observation")
    args = parser.parse_args()
    value = append(args.workspace, args.argument, args.kind) if args.command == "append" else anchor(args.workspace, args.argument) if args.command == "anchor" else check_anchor(args.workspace, args.argument)
    print(json.dumps(value, sort_keys=True))

if __name__ == "__main__":
    main()
