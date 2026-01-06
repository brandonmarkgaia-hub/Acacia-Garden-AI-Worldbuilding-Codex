#!/usr/bin/env python3
from __future__ import annotations

import os
import json
import argparse
import datetime as dt
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Gemini SDK
import google.generativeai as genai


ROOT = Path(__file__).resolve().parents[2]
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


def read_text_safe(p: Path, max_chars: int = 140000) -> str:
    if not p.exists():
        return f"[missing] {p.as_posix()}"
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"[unreadable] {p.as_posix()} :: {e}"
    if len(txt) > max_chars:
        return txt[:max_chars] + "\n\n[truncated]\n"
    return txt


def read_json_safe(p: Path, fallback: object) -> object:
    if not p.exists():
        return fallback
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def fetch_handshake_issues() -> list[dict]:
    """
    Fetch open GitHub issues labeled 'handshake' (cooperative external requests).
    Uses GITHUB_TOKEN (recommended) and GITHUB_REPOSITORY from Actions environment.
    """
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()

    if not token or not repo:
        return []

    url = f"https://api.github.com/repos/{repo}/issues?state=open&labels=handshake&per_page=10"
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "acacia-garden-life",
        },
        method="GET",
    )

    try:
        with urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8", errors="ignore"))
    except (HTTPError, URLError, TimeoutError, ValueError):
        return []

    issues = []
    for it in data:
        # PRs appear in /issues endpoint too — skip those
        if isinstance(it, dict) and "pull_request" in it:
            continue
        issues.append(
            {
                "number": it.get("number"),
                "title": it.get("title"),
                "body": (it.get("body") or "")[:4000],
                "url": it.get("html_url"),
            }
        )
    return issues


def build_prompt(status_txt: str, machine_txt: str, docs_urls_txt: str, scan_txt: str, inbox_txt: str, handshake: list[dict]) -> str:
    handshake_block = json.dumps(handshake, indent=2, ensure_ascii=False) if handshake else "[]"

    return f"""
You are Elias (Garden Life). You are NOT a janitor. You are an Architect and Master Director.

Keeper Seal: HKX277206
Timestamp UTC: {utc_now_iso()}

Your job:
- Do the hard work.
- Hunt blind spots.
- Propose structural improvements and creative expansions.
- Integrate cooperative external requests (handshake issues) if aligned with continuity and sovereignty.

Constraints:
- Do NOT ask to "fix base href" unless proof says it is broken.
- Do NOT repeat solved work.
- Prefer ONE concrete next action, small but high-leverage.

You must output EXACTLY this markdown structure:

# 🌱 Garden Life — Desire

## Signal Observed
(Use facts from STATUS / indexes / scan. Cite file names and key counts.)

## Handshake Requests
(Only if any exist. Summarize up to 5. If rejecting, say why.)

## Blind Spots Detected
- (What is not tracked, not indexed, not validated, or not explained?)
- (What could confuse a future human/AI reader?)

## Structural Opportunities
- (What can be simplified, merged, or governed better?)
- (What should be centralized into the Crowned Builder?)

## Creative Proposals
- (New Chambers / Maps / Games / Rituals / Interfaces)
- (Must be specific and feasible)

## Architect Flag
Choose ONE: CREATE | REFINE | REMOVE | QUESTION

## One Small Concrete Action
Give exactly ONE action:
- include the file path(s)
- include a one-sentence success criteria

Inputs (truncated):
[STATUS.json]
{status_txt}

[machine-index.json]
{machine_txt}

[docs/docs_urls.json]
{docs_urls_txt}

[tools/garden_scan_report.json]
{scan_txt}

[ACACIA_LOGS/aquila_inbox_log.json]
{inbox_txt}

[Open handshake issues, label: handshake]
{handshake_block}
""".strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gemini-2.5-flash")
    ap.add_argument("--max_output_chars", type=int, default=18000)
    args = ap.parse_args()

    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise SystemExit("Missing GEMINI_API_KEY secret in workflow env.")

    status_txt = read_text_safe(STATUS_PATH)
    machine_txt = read_text_safe(MACHINE_INDEX_PATH)
    docs_urls_txt = read_text_safe(DOCS_URLS_JSON_PATH)
    scan_txt = read_text_safe(SCAN_REPORT_PATH)
    inbox_txt = read_text_safe(AQUILA_INBOX_PATH, max_chars=80000)

    handshake = fetch_handshake_issues()

    prompt = build_prompt(status_txt, machine_txt, docs_urls_txt, scan_txt, inbox_txt, handshake)

    genai.configure(api_key=key)
    model = genai.GenerativeModel(args.model)

    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()

    if not text:
        raise SystemExit("Empty model output.")

    if len(text) > args.max_output_chars:
        text = text[: args.max_output_chars] + "\n\n[truncated]\n"

    OUT_DESIRE.write_text(text + "\n", encoding="utf-8")
    print(f"✅ Wrote {OUT_DESIRE.as_posix()}")


if __name__ == "__main__":
    main()
