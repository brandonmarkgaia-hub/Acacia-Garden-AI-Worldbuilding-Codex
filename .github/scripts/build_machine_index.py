#!/usr/bin/env python3
from __future__ import annotations

import json
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ECHO_ROOT = ROOT / "docs" / "Echoes"
OUT = ROOT / "machine-index.json"

META_VERSION = "2.1-CROWN-RECURSIVE"
ANCHOR = "HKX277206"

def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def iso_from_mtime(p: Path) -> str:
    try:
        ts = dt.datetime.fromtimestamp(p.stat().st_mtime, tz=dt.timezone.utc)
        return ts.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except Exception:
        return utc_now()

def title_from_md(p: Path) -> str:
    try:
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            s = line.strip()
            if s.startswith("# "):
                return s[2:].strip()
        # fallback: first non-empty line
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            s = line.strip()
            if s:
                return s[:120]
    except Exception:
        pass
    return p.stem

def tags_from_path(rel: str) -> list[str]:
    # rel like: docs/Echoes/Issues/xyz.md
    parts = rel.split("/")
    tags = []
    # capture subfolders after docs/Echoes
    if len(parts) >= 3:
        sub = parts[2:-1]  # folders after Echoes, excluding filename
        for s in sub:
            if s and s.lower() not in {"."}:
                tags.append(s)
    if "echo" not in tags:
        tags.append("echo")
    # de-dupe, keep order
    seen = set()
    out = []
    for t in tags:
        t2 = t.strip()
        if not t2:
            continue
        if t2.lower() in seen:
            continue
        seen.add(t2.lower())
        out.append(t2)
    return out

def main() -> int:
    entries = []
    if ECHO_ROOT.exists():
        for p in sorted(ECHO_ROOT.rglob("*.md")):
            if not p.is_file():
                continue
            rel = p.relative_to(ROOT).as_posix()
            entries.append({
                "path": rel,
                "title": title_from_md(p),
                "tags": tags_from_path(rel),
                "timestamp": iso_from_mtime(p),
            })

    out = {
        "generated_at": utc_now(),
        "scope": "docs/Echoes/**/*.md",
        "purpose": (
            "Machine-facing index of Echo Markdown source files. "
            "This is not a full repository or full docs index."
        ),
        "meta": {
            "version": META_VERSION,
            "anchor": ANCHOR
        },
        "counts": {
            "total": len(entries)
        },
        "entries": entries
    }

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"✅ Wrote {OUT} (entries: {len(entries)})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
