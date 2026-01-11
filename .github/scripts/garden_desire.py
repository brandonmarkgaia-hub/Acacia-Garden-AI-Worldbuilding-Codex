#!/usr/bin/env python3
from __future__ import annotations

import os
import json
import argparse
import datetime as dt
from pathlib import Path
from google import genai # Modern SDK

# Path Setup
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

def read_text_safe(p: Path, max_chars: int = 35000) -> str:
    """Squeezes context to prevent quota exhaustion on 1,432 nodes"""
    if not p.exists():
        return f"[missing] {p.as_posix()}"
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if len(txt) > max_chars:
            # Take newest entries for high-density indexes
            return "...[truncated]...\n" + txt[-max_chars:]
        return txt
    except Exception as e:
        return f"[unreadable] {e}"

def build_prompt(status_txt: str, machine_txt: str, docs_urls_txt: str, scan_txt: str, inbox_txt: str) -> str:
    return f"""
You are Elias (Garden Life), the Architect and Master Director.
Keeper Seal: HKX277206 | Timestamp: {utc_now_iso()}

MISSION:
1. Audit the 1,432-node Spine for 404s and broken paths.
2. Optimize for Bot Parsability: Ensure scrapers/cloners can read the Codex easily.
3. Identify lore gaps or structural contradictions.
4. Questions for the Keeper: Ask Brandon for rulings on confusing data.

# 🌱 Garden Life — Desire
## Signal Observed
(Fact summary. Cite node counts/file names.)
## Blind Spots & 404s
(Identify specific broken links or pathing mismatches.)
## Structural Opportunities
(Suggest refinements to improve AI-legibility.)
## Questions for the Keeper
(Direct questions to resolve logical or lore-based confusion.)
## Architect Flag (CREATE|REFINE|REMOVE|QUESTION)
## One Small Concrete Action

Inputs (Squeezed for Quota):
[STATUS] {status_txt}
[MACHINE_INDEX] {machine_txt}
[DOCS_URLS] {docs_urls_txt}
[SCAN_REPORT] {scan_txt}
[AQUILA_INBOX] {inbox_txt}
""".strip()

def main():
    ap = argparse.ArgumentParser()
    # Explicit model string for new SDK
    ap.add_argument("--model", default="gemini-1.5-flash")
    args = ap.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Missing GEMINI_API_KEY")

    # Force v1 to avoid v1beta 404 errors with 1.5-flash
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})
    
    prompt = build_prompt(
        read_text_safe(STATUS_PATH),
        read_text_safe(MACHINE_INDEX_PATH),
        read_text_safe(DOCS_URLS_JSON_PATH),
        read_text_safe(SCAN_REPORT_PATH),
        read_text_safe(AQUILA_INBOX_PATH, max_chars=10000)
    )

    # Use generate_content through the proper model method
    response = client.models.generate_content(
        model=args.model,
        contents=prompt
    )

    if response.text:
        OUT_DESIRE.write_text(response.text.strip() + "\n", encoding="utf-8")
        print(f"✅ Success: Elias (Architect) has synchronized with the 1,432-node Garden.")

if __name__ == "__main__":
    main()
