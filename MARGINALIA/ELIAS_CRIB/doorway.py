#!/usr/bin/env python3
"""Read-only source doorway for Elias Crib.

FICTIONAL / NON-EVIDENTIARY: this is a document inspection utility, not an agent.
"""
import argparse
import hashlib
import json
from pathlib import Path

MAX_BYTES = 1024 * 1024

def read_source(repo_root, relative_path, expected_sha256=None):
    root = Path(repo_root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Repository root must be a directory")
    rel = Path(relative_path)
    if rel.is_absolute() or not rel.parts or any(p in (".", "..") for p in rel.parts):
        raise ValueError("Source must be a relative file path")
    source = root / rel
    resolved = source.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError("Source escapes repository")
    if not resolved.is_file() or resolved.suffix.lower() not in (".md", ".txt", ".json"):
        raise ValueError("Unsupported source")
    if resolved.stat().st_size > MAX_BYTES:
        raise ValueError("Source exceeds size limit")
    data = resolved.read_bytes()
    if len(data) > MAX_BYTES:
        raise ValueError("Source exceeds size limit")
    digest = hashlib.sha256(data).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError("Source hash mismatch")
    content = data.decode("utf-8")
    return {
        "source": rel.as_posix(),
        "sha256": digest,
        "bytes": len(data),
        "read_only": True,
        "evidence_status": "source-document-not-independent-verification",
        "canon_status": "unclassified",
        "content": content,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root")
    parser.add_argument("relative_path")
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()
    print(json.dumps(read_source(args.repo_root, args.relative_path, args.expected_sha256),
                     ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
