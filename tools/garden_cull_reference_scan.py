#!/usr/bin/env python3
"""Read-only conservative inbound-reference scan for a proposed cull."""
import json, pathlib, subprocess, sys
report = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else "/tmp/garden_cull_preflight.json")
data = json.loads(report.read_text())
rows = data["operations"]
paths = [r["source"] for r in rows]
files = subprocess.check_output(["git","ls-files","-z"]).decode().split("\0")
hits = {p: [] for p in paths}
for name in files:
    if not name or name in paths:
        continue
    f = pathlib.Path(name)
    if not f.is_file() or f.stat().st_size > 2_000_000:
        continue
    try:
        body = f.read_text(encoding="utf-8")
    except (UnicodeError, OSError):
        continue
    for p in paths:
        if p in body or pathlib.PurePosixPath(p).name in body:
            hits[p].append(name)
summary = {p: v for p, v in hits.items() if v}
out = report.with_name("garden_cull_inbound_references.json")
out.write_text(json.dumps(summary, indent=2) + "\n")
print(f"{len(summary)} of {len(paths)} proposed paths have possible references in remaining tracked files.")
print("Review", out, "before moving or deleting any source.")
sys.exit(1 if summary else 0)
