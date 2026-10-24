#!/usr/bin/env python3
"""Fail closed on changes to AUTHORITY.json immutable founder record.

Compare PR checkout against the base commit, not a self-generated manifest.
"""
import json
import subprocess
import sys

def git(*args):
    return subprocess.check_output(["git", *args], text=True)

def check(base_ref="origin/main"):
    try:
        before = json.loads(git("show", f"{base_ref}:AUTHORITY.json"))
        after = json.loads(open("AUTHORITY.json", encoding="utf-8").read())
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print("FAIL: cannot verify AUTHORITY.json:", exc, file=sys.stderr)
        return 1
    if "immutable_record" not in before or "immutable_record" not in after:
        print("FAIL: missing immutable_record", file=sys.stderr)
        return 1
    if before["immutable_record"] != after["immutable_record"]:
        print("FAIL: AUTHORITY.json immutable_record changed relative to base", file=sys.stderr)
        return 1
    if after["immutable_record"].get("mutable") is not False:
        print("FAIL: immutable_record.mutable is not false", file=sys.stderr)
        return 1
    print("PASS: AUTHORITY.json immutable_record unchanged relative to base")
    return 0

if __name__ == "__main__":
    sys.exit(check(sys.argv[1] if len(sys.argv) > 1 else "origin/main"))
