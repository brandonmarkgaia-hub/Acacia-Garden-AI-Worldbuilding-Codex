# tools/resonance_mirror.py
# Purpose: Detect orphaned files ("Silent Roots") and broken references ("Phantom Echoes").
# Output: EVOLUTION/RESONANCE_MIRROR_LATEST.json & EVOLUTION/RESONANCE_MIRROR_LATEST.md

import os
import re
import json
from datetime import datetime
from urllib.parse import unquote

ROOT = "./"
OUT_DIR = "EVOLUTION"
MAX_READ_BYTES = 2 * 1024 * 1024

IGNORE_DIRS = {
    ".git", ".github", "__pycache__", "node_modules", ".venv", "venv",
    "dist", "build", "EVOLUTION", ".next", ".cache"
}

SCAN_EXTS = {
    ".md", ".txt", ".json", ".yml", ".yaml", ".html", ".js", ".ts",
    ".mjs", ".cjs", ".py", ".xml", ".css"
}

BODY_EXCLUDE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mov", ".zip", ".pdf", ".ico"}

PATH_RE = re.compile(
    r'(?P<path>(?:\./)?[A-Za-z0-9_\-./]+?\.(?:md|json|html|py|js|yml|yaml|sh|txt|xml|css|mjs|cjs))',
    re.IGNORECASE
)

def _walk(root_dir):
    root_dir = os.path.abspath(root_dir)
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for name in files:
            yield root, name

def _rel(path, root_dir):
    return os.path.relpath(path, root_dir).replace("\\", "/")

def _safe_read(path):
    try:
        if os.stat(path).st_size > MAX_READ_BYTES:
            return ""
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""

def _normalize_ref(raw, from_file_dir=None):
    s = raw.strip().strip('"\''"()[]{}<>.,;")
    s = unquote(s)
    s = s.split("#", 1)[0].split("?", 1)[0]

    if s.startswith("http://") or s.startswith("https://"):
        return None

    if s.startswith("./"):
        s = s[2:]

    if from_file_dir and not s.startswith("/") and not re.match(r"^[A-Za-z]:/", s):
        joined = os.path.normpath(os.path.join(from_file_dir, s)).replace("\\", "/")
        if joined.startswith("./"):
            joined = joined[2:]
        return joined.lstrip("/")

    return s.lstrip("/")

def collect_physical_body(root_dir=ROOT):
    body = set()
    root_dir = os.path.abspath(root_dir)
    for root, name in _walk(root_dir):
        ext = os.path.splitext(name)[1].lower()
        if ext in BODY_EXCLUDE_EXTS:
            continue
        abs_path = os.path.join(root, name)
        body.add(_rel(abs_path, root_dir))
    return body

def extract_neural_memory(root_dir=ROOT):
    referenced = set()
    root_dir = os.path.abspath(root_dir)

    for root, name in _walk(root_dir):
        ext = os.path.splitext(name)[1].lower()
        if ext not in SCAN_EXTS:
            continue

        abs_path = os.path.join(root, name)
        rel_file = _rel(abs_path, root_dir)
        content = _safe_read(abs_path)
        if not content:
            continue

        from_dir = os.path.dirname(rel_file).replace("\\", "/")
        for m in PATH_RE.finditer(content):
            raw = m.group("path")
            norm = _normalize_ref(raw, from_file_dir=from_dir)
            if norm:
                referenced.add(norm)

    return referenced

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    physical = collect_physical_body(ROOT)
    referenced = extract_neural_memory(ROOT)

    silent_roots = sorted(list(physical - referenced))
    phantom_echoes = sorted(list(referenced - physical))

    resonance_score = 0.0
    if physical:
        resonance_score = (1.0 - (len(silent_roots) / len(physical))) * 100.0

    report = {
        "meta": {
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "type": "RESONANCE_MIRROR",
            "policy": "REPORT_ONLY_NO_AUTOMATION"
        },
        "counts": {
            "physical_files": len(physical),
            "referenced_files": len(referenced),
            "silent_roots": len(silent_roots),
            "phantom_echoes": len(phantom_echoes),
            "resonance_score_percent": float(f"{resonance_score:.2f}")
        },
        "silent_roots_sample": silent_roots[:200],
        "phantom_echoes_sample": phantom_echoes[:200],
    }

    json_path = os.path.join(OUT_DIR, "RESONANCE_MIRROR_LATEST.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    md_path = os.path.join(OUT_DIR, "RESONANCE_MIRROR_LATEST.md")
    md = []
    md.append("# Resonance Mirror (Latest)")
    md.append("")
    md.append(f"- Generated (UTC): {report['meta']['timestamp_utc']}")
    md.append(f"- Physical files: **{report['counts']['physical_files']}**")
    md.append(f"- Referenced files: **{report['counts']['referenced_files']}**")
    md.append(f"- Silent roots: **{report['counts']['silent_roots']}**")
    md.append(f"- Phantom echoes: **{report['counts']['phantom_echoes']}**")
    md.append(f"- Resonance score: **{report['counts']['resonance_score_percent']}%**")
    md.append("")
    md.append("## Silent Roots (sample)")
    for p in silent_roots[:30]:
        md.append(f"- {p}")
    if len(silent_roots) > 30:
        md.append(f"- ... +{len(silent_roots) - 30} more")
    md.append("")
    md.append("## Phantom Echoes (sample)")
    for p in phantom_echoes[:30]:
        md.append(f"- {p}")
    if len(phantom_echoes) > 30:
        md.append(f"- ... +{len(phantom_echoes) - 30} more")
    md.append("")
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"✅ Resonance Mirror written: {json_path}")

if __name__ == "__main__":
    main()
