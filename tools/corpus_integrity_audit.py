#!/usr/bin/env python3
"""Read-only, checkout-bound corpus and legacy integrity audit.

Produces reproducible counts and findings. Does not infer Law, validate
Keeper identity, rewrite files, or change CHECKSUMS.sha256.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

SIGNATURE = re.compile(r"<!--SIG-->.*?<!--ENDSIG-->", re.S)
STATUS = re.compile(r"(?im)^\\s*(?:status|canon_status|voice_class)\\s*[:=]")
LINK = re.compile(r"(?<!\\!)\\[[^]]+\\]\\(([^)]+)\\)")


def audit(root):
    root = Path(root).resolve()
    files = sorted(p for p in root.rglob("*") if p.is_file()
                   and ".git" not in p.relative_to(root).parts)
    md = [p for p in files if p.suffix.lower() == ".md"]
    findings = {"schema": "acacia.corpus-audit/1", "status": "advisory_unverified_authorship",
                "checkout_head": None, "markdown_files": len(md),
                "empty_or_short_markdown": [], "signature_footers": 0,
                "files_with_status_marker": 0, "relative_markdown_links_missing": [],
                "checksum": {"listed": 0, "checked": 0, "mismatches": [], "missing": [], "invalid_lines": []},
                "limits": ["No semantic classification", "No authentication of Keeper",
                           "Link check covers only simple Markdown links",
                           "Checksum format is sha256sum-compatible lines only"]}
    try:
        findings["checkout_head"] = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        pass
    for p in md:
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        without_footer = SIGNATURE.sub("", text).strip()
        if len(without_footer) < 300:
            findings["empty_or_short_markdown"].append(rel)
        if SIGNATURE.search(text):
            findings["signature_footers"] += 1
        if STATUS.search(text[:1600]):
            findings["files_with_status_marker"] += 1
        for target in LINK.findall(text):
            target = target.split("#", 1)[0].split("?", 1)[0]
            if not target or "://" in target or target.startswith(("/", "#", "mailto:", "data:")):
                continue
            if "%" in target:
                continue
            if not (p.parent / target).resolve().is_relative_to(root):
                continue
            if not (p.parent / target).exists():
                findings["relative_markdown_links_missing"].append({"source": rel, "target": target})
    checks = root / "CHECKSUMS.sha256"
    if checks.exists():
        for line_number, line in enumerate(checks.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            match = re.fullmatch(r"([a-fA-F0-9]{64})  [*]?(.+)", line)
            if not match:
                findings["checksum"]["invalid_lines"].append(line_number)
                continue
            digest, path = match.groups()
            findings["checksum"]["listed"] += 1
            candidate = (root / path).resolve()
            if not candidate.is_relative_to(root) or not candidate.is_file():
                findings["checksum"]["missing"].append(path)
                continue
            findings["checksum"]["checked"] += 1
            if hashlib.sha256(candidate.read_bytes()).hexdigest() != digest.lower():
                findings["checksum"]["mismatches"].append(path)
    findings["short_count"] = len(findings["empty_or_short_markdown"])
    findings["missing_link_count"] = len(findings["relative_markdown_links_missing"])
    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = json.dumps(audit(args.root), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
