#!/usr/bin/env python3
"""Report Markdown files with little or no meaningful source content."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "docs" / "Archives" / "EMPTY_MARKDOWN_AUDIT.json"
OUT_MD = ROOT / "docs" / "Archives" / "EMPTY_MARKDOWN_AUDIT.md"
EXCLUDE_DIRS = {".git", ".github", "node_modules", "dist", "machine", "scripts", ".well-known"}
THRESHOLD = 80

SIG_RE = re.compile(r"<!--SIG-->.*?<!--ENDSIG-->", re.S)
FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.S)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
TAG_RE = re.compile(r"<[^>]+>")
MARKUP_ONLY_RE = re.compile(r"^[#>*_~|:\-\s:]+$")

def meaningful(text: str) -> str:
    text = SIG_RE.sub("", text)
    text = FRONTMATTER_RE.sub("", text, count=1)
    text = COMMENT_RE.sub("", text)
    text = TAG_RE.sub(" ", text)
    kept = []
    for line in text.splitlines():
        line = line.strip()
        if not line or MARKUP_ONLY_RE.fullmatch(line):
            continue
        kept.append(line)
    return " ".join(kept).strip()

def main() -> int:
    rows = []
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT)
        rels = rel.as_posix()
        if any(part in EXCLUDE_DIRS for part in rel.parts) or rels.startswith("docs/Archives/"):
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        body = meaningful(raw)
        if len(body) <= THRESHOLD:
            rows.append({
                "path": rels,
                "bytes": path.stat().st_size,
                "meaningful_chars": len(body),
                "meaningful_text": body[:160],
                "classification": "review",
            })

    report = {
        "schema": "acacia-empty-markdown-audit/v1",
        "scope": "Markdown source files outside generated/archive and tooling directories",
        "threshold_meaningful_chars": THRESHOLD,
        "deletion_policy": "report_only",
        "count": len(rows),
        "files": rows,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Empty / Near-Empty Markdown Audit",
        "",
        "Report only — no files are deleted or rewritten by this audit.",
        "",
        f"- Review candidates: {len(rows)}",
        f"- Threshold: meaningful content <= {THRESHOLD} characters",
        "- Signature blocks, frontmatter, HTML comments, markup-only lines and generated/archive directories are excluded.",
        "",
    ]
    for row in rows:
        preview = row["meaningful_text"].replace("\n", " ")
        suffix = f" — {preview}" if preview else ""
        lines.append(f"- `{row['path']}` — {row['bytes']} bytes, {row['meaningful_chars']} meaningful chars{suffix}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[EMPTY-AUDIT] Review candidates: {len(rows)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
