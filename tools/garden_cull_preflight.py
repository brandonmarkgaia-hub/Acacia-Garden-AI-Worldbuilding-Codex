#!/usr/bin/env python3
"""Read-only verification of a proposed cull.sh; no repository mutations."""
import argparse, hashlib, json, pathlib, re, subprocess, sys

def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()

parser = argparse.ArgumentParser()
parser.add_argument("--script", default="cull.sh")
parser.add_argument("--report", default="/tmp/garden_cull_preflight.json")
args = parser.parse_args()
script = pathlib.Path(args.script).read_text()
operations = re.findall(r'^([dq]) "([^"]+)"\s*$', script, re.M)
errors, rows = [], []
operation_lines = [line.strip() for line in script.splitlines() if re.match(r"^[dq](?=\\s|[\"\x27]|$)", line.strip())]
parsed_lines = [f'{action} "{source}"' for action, source in operations]
if operation_lines != parsed_lines:
    errors.append("Unparsed or malformed cull operation line; fail closed")
for _, source in operations:
    p = pathlib.PurePosixPath(source)
    if (p.is_absolute() or ".." in p.parts or "." in p.parts or
            "\\" in source or source.startswith("-") or
            p.as_posix() != source or not source.strip()):
        errors.append("Unsafe source path: " + source)

if len(operations) != 242 or len({p for _, p in operations}) != 242:
    errors.append("Expected 242 distinct operations")
if sum(k == "d" for k, _ in operations) != 61 or sum(k == "q" for k, _ in operations) != 181:
    errors.append("Unexpected delete/move counts")
try:
    branch = git("branch", "--show-current")
    if branch in ("", "main", "master"):
        errors.append("Refusing default branch or detached HEAD")
    tracked = set(git("ls-files", "-z").split("\\0"))
    dirty = [line for line in git("status", "--porcelain").splitlines() if line[3:] != args.script]
    if dirty:
        errors.append("Working tree not clean except cull script")
except Exception as exc:
    branch = "unknown"
    tracked = set()
    errors.append("Git preflight failed: " + str(exc))
for action, source in operations:
    path = pathlib.Path(source)
    if (path.is_absolute() or ".." in path.parts or
            "\\" in source or source.startswith("-")):
        continue
    if any(parent.is_symlink() for parent in path.parents if parent != pathlib.Path(".")):
        errors.append("Symlink parent directory: " + source)
        continue
    if source not in tracked:
        errors.append("Source is not tracked by Git: " + source)
        continue
    if path.is_symlink() or not path.is_file():
        errors.append("Missing or symlink source: " + source)
        continue
    raw = path.read_bytes()
    row = {"action": "delete" if action == "d" else "archive",
           "source": source, "sha256": hashlib.sha256(raw).hexdigest(),
           "bytes": len(raw)}
    if action == "q":
        dest = pathlib.Path("_ROOT_ARCHIVE/generated_era") / source
        row["destination"] = dest.as_posix()
        if dest.exists() or dest.as_posix() in tracked:
            errors.append("Destination already exists: " + str(dest))
    elif source.startswith("MUTATIONS/MUTATION_"):
        twin = pathlib.Path("MUTATIONS") / path.name.removeprefix("MUTATION_")
        if not twin.is_file() or twin.read_bytes() != raw:
            errors.append("Not an identical duplicate: " + source)
        else:
            row["identical_copy"] = twin.as_posix()
    else:
        row["manual_review_required"] = True
    rows.append(row)
manual = [r["source"] for r in rows if r.get("manual_review_required")]
pathlib.Path(args.report).write_text(json.dumps({
    "branch": branch, "operations": rows, "errors": errors,
    "manual_review_deletions": manual}, indent=2) + "\n")
print(f"Preflight: {len(rows)}/{len(operations)} files; "
      f"{len(errors)} errors; {len(manual)} manual deletion reviews.")
for error in errors[:20]:
    print("BLOCK:", error)
if errors or manual:
    sys.exit(1)
