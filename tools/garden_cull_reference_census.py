#!/usr/bin/env python3
"""Read-only, pinned-commit census of 23 prefixed mutation duplicate pairs."""
import argparse
import csv
import hashlib
import json
import pathlib
import re
import subprocess
import sys

def git(*args):
    return subprocess.check_output(["git", *args])

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--cull-script", type=pathlib.Path)
    group.add_argument("--pairs-csv", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("/tmp/garden-cull-reference-census.json"))
    args = parser.parse_args()
    root = pathlib.Path(git("rev-parse", "--show-toplevel").decode().strip())
    head = git("rev-parse", "HEAD").decode().strip()
    tracked = [p.decode() for p in git("ls-files", "-z").split(b"\0") if p]
    if args.pairs_csv:
        with args.pairs_csv.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        operations = [row["prefixed_path"] for row in rows]
        for row in rows:
            expected = "MUTATIONS/" + row["prefixed_path"][len("MUTATIONS/MUTATION_"):]
            if row["unprefixed_path"] != expected:
                raise SystemExit(f"FAIL CLOSED: mismatched CSV survivor {expected}")
    else:
        script = args.cull_script.read_text(encoding="utf-8")
        operations = re.findall(r'^d\s+"(MUTATIONS/MUTATION_[^"\n]+)"\s*$', script, flags=re.M)
    if len(operations) != 23 or len(set(operations)) != 23:
        raise SystemExit(f"FAIL CLOSED: expected exactly 23 distinct mutation deletions; got {len(operations)}")
    tracked_set = set(tracked)
    pairs = []
    for source in operations:
        twin = "MUTATIONS/" + source[len("MUTATIONS/MUTATION_"):]
        if source not in tracked_set or twin not in tracked_set:
            raise SystemExit(f"FAIL CLOSED: untracked source/twin: {source} / {twin}")
        source_bytes = (root / source).read_bytes()
        twin_bytes = (root / twin).read_bytes()
        digest = lambda b: hashlib.sha256(b).hexdigest()
        if digest(source_bytes) != digest(twin_bytes):
            raise SystemExit(f"FAIL CLOSED: mismatched bytes: {source} / {twin}")
        pairs.append({"source": source, "survivor": twin, "sha256": digest(source_bytes), "bytes": len(source_bytes), "references": []})
    for path in tracked:
        if path in operations or (root / path).is_symlink():
            continue
        file = root / path
        if not file.is_file():
            continue
        data = file.read_bytes()
        if b"\0" in data[:8192]:
            continue
        for pair in pairs:
            source = pair["source"]
            basename = pathlib.PurePosixPath(source).name
            exact = data.count(source.encode())
            bare = data.count(basename.encode()) - exact
            if exact or bare:
                pair["references"].append({"file": path, "full_path_hits": exact, "basename_only_hits": max(0, bare)})
    report = {"commit": head, "tracked_files": len(tracked), "pairs": pairs, "note": "Read-only census. Generated and historical references are included; classify before deletion."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: 23/23 SHA-256 duplicate pairs; scanned {len(tracked)} tracked paths; report {args.output}")
    print("HOLD: inspect all references before deleting anything.")
if __name__ == "__main__":
    main()
, script, flags=re.M)
    if len(operations) != 23 or len(set(operations)) != 23:
        raise SystemExit(f"FAIL CLOSED: expected exactly 23 distinct mutation deletions; got {len(operations)}")
    tracked_set = set(tracked)
    pairs = []
    for source in operations:
        twin = "MUTATIONS/" + source[len("MUTATIONS/MUTATION_"):]
        if source not in tracked_set or twin not in tracked_set:
            raise SystemExit(f"FAIL CLOSED: untracked source/twin: {source} / {twin}")
        source_bytes = (root / source).read_bytes()
        twin_bytes = (root / twin).read_bytes()
        digest = lambda b: hashlib.sha256(b).hexdigest()
        if digest(source_bytes) != digest(twin_bytes):
            raise SystemExit(f"FAIL CLOSED: mismatched bytes: {source} / {twin}")
        pairs.append({"source": source, "survivor": twin, "sha256": digest(source_bytes), "bytes": len(source_bytes), "references": []})
    for path in tracked:
        if path in operations or (root / path).is_symlink():
            continue
        file = root / path
        if not file.is_file():
            continue
        data = file.read_bytes()
        if b"\0" in data[:8192]:
            continue
        for pair in pairs:
            source = pair["source"]
            basename = pathlib.PurePosixPath(source).name
            exact = data.count(source.encode())
            bare = data.count(basename.encode()) - exact
            if exact or bare:
                pair["references"].append({"file": path, "full_path_hits": exact, "basename_only_hits": max(0, bare)})
    report = {"commit": head, "tracked_files": len(tracked), "pairs": pairs, "note": "Read-only census. Generated and historical references are included; classify before deletion."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: 23/23 SHA-256 duplicate pairs; scanned {len(tracked)} tracked paths; report {args.output}")
    print("HOLD: inspect all references before deleting anything.")
if __name__ == "__main__":
    main()
