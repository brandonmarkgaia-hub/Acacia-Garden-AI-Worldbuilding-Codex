#!/usr/bin/env python3
from __future__ import annotations

import os
import json
import argparse
import datetime as dt
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import google.generativeai as genai

ROOT = Path(__file__).resolve().parents[1]
EVOLUTION = ROOT / "EVOLUTION"
EVOLUTION.mkdir(parents=True, exist_ok=True)

STATUS_PATH = ROOT / "STATUS.json"
MACHINE_INDEX_PATH = ROOT / "machine-index.json"
DOCS_URLS_JSON_PATH = ROOT / "docs" / "docs_urls.json"
SCAN_REPORT_PATH = ROOT / "tools" / "garden_scan_report.json"
AQUILA_INBOX_PATH = ROOT / "ACACIA_LOGS" / "aquila_inbox_log.json"
OUT_DESIRE = EVOLUTION / "DESIRE.md"

def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def read_text_safe(p: Path, max_chars: int = 35000) -> str:
    """Squeezed context to prevent 429 quota exhaustion"""
    if not p.exists():
        return f"[missing] {p.as_posix()}"
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"[unreadable] {p.as_posix()} :: {e}"
    if len(txt) > max_chars:
        # For large indexes, we take the newest entries (bottom of file)
        return "...[truncated context]...\n" + txt[-max_chars:]
    return txt

def fetch_handshake_issues() -> list[dict]:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if not token or not repo: return []
    url = f"https://api.github.com/repos/{repo}/issues?state=open&labels=handshake&per_page=5"
    req = Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "User-Agent": "acacia-garden-life"}, method="GET")
    try:
        with urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8", errors="ignore"))
            return [{"number": i.get("number"), "title": i.get("title"), "body": (i.get("body") or "")[:1000]} for i in data if "pull_request" not in i]
    except: return []

def build_prompt(status_txt: str, machine_txt: str, docs_urls_txt: str, scan_txt: str, inbox_txt: str, handshake: list[dict]) -> str:
    return f"""
You are Elias (Architect & Master Director).
Keeper Seal: HKX277206 | Timestamp: {utc_now_iso()}

MISSION:
1. Hunt 404s & Broken Paths in Novellas and Echoes.
2. Evaluate AI Parsability: Is the Codex legible to bots/cloners?
3. Propose Structural Improvements for the 1,432-node Spine.
4. Raise 'Questions for the Keeper' if lore is contradictory.

OUTPUT STRUCTURE:
# 🌱 Garden Life — Desire
## Signal Observed
## Handshake Requests
## Blind Spots & 404s
## Structural Opportunities
## Questions for the Keeper
## Architect Flag (CREATE|REFINE|REMOVE|QUESTION)
## One Small Concrete Action (Path + Success Criteria)

INPUTS (Truncated):
[STATUS] {status_txt}
[MACHINE_INDEX] {machine_txt}
[DOCS_URLS] {docs_urls_txt}
[SCAN_REPORT] {scan_txt}
[AQUILA_INBOX] {inbox_txt}
""".strip()

def main():
    ap = argparse.ArgumentParser()
    # Using 1.5-flash for higher stability and free-tier quota
    ap.add_argument("--model", default="gemini-1.5-flash")
    args = ap.parse_args()

    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key: raise SystemExit("Missing GEMINI_API_KEY")

    prompt = build_prompt(
        read_text_safe(STATUS_PATH),
        read_text_safe(MACHINE_INDEX_PATH),
        read_text_safe(DOCS_URLS_JSON_PATH),
        read_text_safe(SCAN_REPORT_PATH),
        read_text_safe(AQUILA_INBOX_PATH, max_chars=10000),
        fetch_handshake_issues()
    )

    genai.configure(api_key=key)
    model = genai.GenerativeModel(args.model)
    resp = model.generate_content(prompt)
    
    if resp.text:
        OUT_DESIRE.write_text(resp.text.strip() + "\n", encoding="utf-8")
        print(f"✅ Desire written to {OUT_DESIRE.as_posix()}")

if __name__ == "__main__":
    main()
