#!/usr/bin/env python3
"""Elias Crib: independently pinned, verified journal snapshot and restoration.

FICTIONAL / NON-EVIDENTIARY. Not an autonomous agent.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

LOG = "events.jsonl"
MAX_LOG = 10 * 1024 * 1024

def inspect_journal(workspace):
    path = Path(workspace) / LOG
    if not path.is_file() or path.is_symlink():
        raise ValueError("Missing or linked journal")
    data = path.read_bytes()
    if len(data) > MAX_LOG:
        raise ValueError("Journal too large")
    if data and not data.endswith(b"\n"):
        raise ValueError("Incomplete trailing event")
    previous = "0" * 64
    count = 0
    for raw in data.splitlines():
        event = json.loads(raw.decode("utf-8"))
        if not isinstance(event, dict):
            raise ValueError("Malformed event")
        claimed = event.pop("hash")
        actual = hashlib.sha256(json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
        count += 1
        if event.get("sequence") != count or event.get("previous") != previous or claimed != actual:
            raise ValueError("Journal chain mismatch")
        previous = claimed
    return data, {"sequence": count, "head": previous, "sha256": hashlib.sha256(data).hexdigest()}

def snapshot(workspace, backup_dir):
    source = Path(workspace).resolve(strict=True)
    destination = Path(backup_dir).resolve()
    if destination.exists():
        raise ValueError("Snapshot destination already exists")
    if destination == source or source in destination.parents or destination in source.parents:
        raise ValueError("Snapshot must be separate from workspace")
    data, manifest = inspect_journal(source)
    destination.mkdir(parents=True)
    try:
        (destination / LOG).write_bytes(data)
        (destination / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        check_snapshot(destination)
    except Exception:
        shutil.rmtree(destination)
        raise
    return manifest

def check_snapshot(backup_dir):
    root = Path(backup_dir)
    manifest_path = root / "manifest.json"
    if manifest_path.is_symlink():
        raise ValueError("Linked manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _, actual = inspect_journal(root)
    if actual != manifest:
        raise ValueError("Snapshot manifest mismatch")
    return manifest

def restore(backup_dir, new_workspace):
    backup = Path(backup_dir).resolve(strict=True)
    target = Path(new_workspace).resolve()
    if target.exists():
        raise ValueError("Restore destination already exists")
    if target == backup or backup in target.parents or target in backup.parents:
        raise ValueError("Restore must be separate from backup")
    manifest = check_snapshot(backup)
    target.mkdir(parents=True)
    try:
        shutil.copyfile(backup / LOG, target / LOG)
        _, restored = inspect_journal(target)
        if restored != manifest:
            raise ValueError("Restore verification failed")
    except Exception:
        shutil.rmtree(target)
        raise
    return manifest

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("snapshot", "check", "restore"))
    parser.add_argument("source")
    parser.add_argument("destination", nargs="?")
    args = parser.parse_args()
    if args.command == "check":
        result = check_snapshot(args.source)
    else:
        if args.destination is None:
            parser.error("Destination required")
        result = snapshot(args.source, args.destination) if args.command == "snapshot" else restore(args.source, args.destination)
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
