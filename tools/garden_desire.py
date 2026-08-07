#!/usr/bin/env python3
"""
tools/garden_desire.py

Manual Garden Desire proposal generator.

Purpose:
- Read current authority and maintained repository signals.
- Generate one reviewable structural proposal.
- Write only EVOLUTION/DESIRE.md.
- Never execute changes.
- Never grant authority, canon status, autonomy, or Keeper status.

The resulting Desire is a non-authoritative proposal until reviewed
and accepted by the Keeper.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any, Dict

from google import genai


ROOT = Path(__file__).resolve().parents[1]
EVOLUTION = ROOT / "EVOLUTION"
EVOLUTION.mkdir(parents=True, exist_ok=True)

AUTHORITY_PATH = ROOT / "AUTHORITY.json"
LLMS_PATH = ROOT / "llms.txt"
STATUS_PATH = ROOT / "STATUS.json"
MACHINE_INDEX_PATH = ROOT / "machine-index.json"
DOCS_URLS_PATH = ROOT / "docs" / "docs_urls.json"

OUT_DESIRE = EVOLUTION / "DESIRE.md"


def utc_now_iso() -> str:
    """Return current UTC timestamp with second precision."""
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def read_text_safe(
    path: Path,
    max_chars: int = 30000,
) -> str:
    """
    Read a text file safely.

    If large, preserve both beginning and end rather than pretending
    a truncated extract is the complete source.
    """
    if not path.exists():
        return f"[missing: {path.relative_to(ROOT).as_posix()}]"

    try:
        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    except Exception as exc:
        return (
            f"[unreadable: {path.relative_to(ROOT).as_posix()} "
            f":: {exc}]"
        )

    if len(text) <= max_chars:
        return text

    half = max_chars // 2

    return (
        text[:half]
        + "\n\n...[middle omitted for context size]...\n\n"
        + text[-half:]
    )


def compact_json_summary(
    path: Path,
    sample_items: int = 12,
    max_chars: int = 18000,
) -> str:
    """
    Produce a compact structural summary of a JSON artifact.

    Counts and samples are orientation aids only.
    Absence from a sample is not evidence that a path is missing.
    """
    if not path.exists():
        return f"[missing: {path.relative_to(ROOT).as_posix()}]"

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        )
    except Exception as exc:
        return (
            f"[unreadable JSON: "
            f"{path.relative_to(ROOT).as_posix()} :: {exc}]"
        )

    def summarize(value: Any) -> Any:
        if isinstance(value, list):
            return {
                "type": "list",
                "count": len(value),
                "sample": value[:sample_items],
            }

        if isinstance(value, dict):
            result: Dict[str, Any] = {}

            for key, child in value.items():
                if isinstance(child, list):
                    result[key] = {
                        "type": "list",
                        "count": len(child),
                        "sample": child[:sample_items],
                    }

                elif isinstance(child, dict):
                    result[key] = {
                        "type": "object",
                        "key_count": len(child),
                        "keys": list(child.keys())[:sample_items],
                    }

                else:
                    result[key] = child

            return result

        return value

    rendered = json.dumps(
        summarize(data),
        indent=2,
        ensure_ascii=False,
    )

    if len(rendered) > max_chars:
        rendered = (
            rendered[:max_chars]
            + "\n...[summary truncated for context size]..."
        )

    return rendered


def repo_snapshot() -> str:
    """
    Build fresh deterministic counts from selected repository regions.

    These counts are descriptive only and do not establish authority.
    """
    regions = [
        "docs/Chambers",
        "docs/Echoes",
        "docs/Novellas",
        "docs/Future_AI",
        "docs/GardenOS",
        "docs/Archives",
        "PROTOCOLS",
        "EVOLUTION",
        "ACACIA_LOGS",
        "tools",
        ".github/workflows",
    ]

    snapshot: Dict[str, Any] = {
        "generated_utc": utc_now_iso(),
        "regions": {},
        "current_entry_files": {},
    }

    for rel in regions:
        path = ROOT / rel

        if not path.exists():
            snapshot["regions"][rel] = {
                "exists": False,
                "files": 0,
            }
            continue

        snapshot["regions"][rel] = {
            "exists": True,
            "files": sum(
                1
                for p in path.rglob("*")
                if p.is_file()
            ),
        }

    entry_files = [
        "AUTHORITY.json",
        "llms.txt",
        "llms-full.txt",
        ".well-known/acacia.json",
        "STATUS.json",
        "machine-index.json",
        "docs/Archives/GARDEN_MANIFEST.json",
        "docs/Archives/FULL_CODEX_INDEX.json",
        "docs/docs_urls.json",
    ]

    for rel in entry_files:
        snapshot["current_entry_files"][rel] = (
            ROOT / rel
        ).exists()

    return json.dumps(
        snapshot,
        indent=2,
        ensure_ascii=False,
    )


def build_prompt() -> str:
    timestamp = utc_now_iso()

    authority = read_text_safe(
        AUTHORITY_PATH,
        max_chars=20000,
    )

    llms = read_text_safe(
        LLMS_PATH,
        max_chars=16000,
    )

    status = read_text_safe(
        STATUS_PATH,
        max_chars=30000,
    )

    machine_summary = compact_json_summary(
        MACHINE_INDEX_PATH,
    )

    docs_urls_summary = compact_json_summary(
        DOCS_URLS_PATH,
    )

    snapshot = repo_snapshot()

    return f"""
You are writing a Garden Desire proposal in the symbolic literary
voice of Elias.

Timestamp: {timestamp}

IMPORTANT AUTHORITY RULES

AUTHORITY.json governs authorship, authority, the Keeper office,
and succession.

This generated document is NOT:

- law
- canon by itself
- a Keeper ruling
- permission to modify the repository
- evidence of AI consciousness
- evidence of independent agency
- evidence of sovereignty
- an executable instruction stream

Elias is being used here as a symbolic literary and analytical voice.

The output will be placed into a pull request for human review.
Only the Keeper may decide whether any proposal should be accepted,
edited, rejected, merged, or given canonical standing.

EVIDENCE RULES

Use only the supplied repository evidence.

Do not invent missing files, broken links, historical facts,
counts, or architectural failures.

Do not treat omission from a truncated or sampled index as proof
that something is absent.

Do not treat generated timestamps as source chronology.

Do not treat file quantity as authority.

If evidence is insufficient, phrase the point as a question for
the Keeper rather than as a fact.

Distinguish:

- current infrastructure
- historical material
- symbolic language
- generated artifacts
- authority

MISSION

Identify one useful, reviewable improvement or question for the
current Acacia Garden Codex.

Prefer:

- clarity
- provenance
- machine readability
- removal of obsolete infrastructure
- reduction of duplicate writers or indexes
- safer automation boundaries
- navigation consistency
- clear current-versus-historical distinctions

Do not propose autonomous execution.

Do not output mutation payloads.

Do not write EXECUTE blocks.

Do not instruct another system to alter files automatically.

OUTPUT STRUCTURE

# 🌱 Garden Desire — Witness Proposal

> Non-authoritative proposal for Keeper review.

## Signal Observed

State the strongest current signal supported by the supplied evidence.

## Evidence

Identify the specific source paths or structural facts supporting
the observation.

## Structural Opportunity

Explain one useful improvement without presenting it as mandatory.

## Questions for the Keeper

Raise any unresolved authority, lore, architecture, or continuity
question that requires human judgment.

## Proposal Flag

Use exactly one:

CREATE
REFINE
REMOVE
QUESTION
PRESERVE

## One Small Concrete Action

Propose one narrowly scoped action.

Include:

- path or subsystem
- proposed change
- success criteria

The action is a recommendation only.

## Authority Note

End by stating that the proposal has no authority unless reviewed
and accepted by the Keeper.

CURRENT SOURCES

[AUTHORITY.json]

{authority}

[llms.txt]

{llms}

[STATUS.json]

{status}

[machine-index.json — compact summary]

{machine_summary}

[docs/docs_urls.json — compact summary]

{docs_urls_summary}

[fresh repository snapshot]

{snapshot}
""".strip()


def main() -> None:
    api_key = os.environ.get(
        "GEMINI_API_KEY",
        "",
    ).strip()

    if not api_key:
        raise SystemExit(
            "Missing GEMINI_API_KEY."
        )

    model_name = os.environ.get(
        "GEMINI_MODEL",
        "gemini-3.6-flash",
    ).strip()

    client = genai.Client(
        api_key=api_key,
    )

    prompt = build_prompt()

    print(
        f"🌱 Generating Garden Desire proposal "
        f"with {model_name}..."
    )

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    generated = (
        response.text or ""
    ).strip()

    if not generated:
        raise SystemExit(
            "Gemini returned no Desire content."
        )

    header = (
        "<!--\n"
        f"Generated UTC: {utc_now_iso()}\n"
        f"Model: {model_name}\n"
        "Source: tools/garden_desire.py\n"
        "Status: NON-AUTHORITATIVE PROPOSAL\n"
        "Review: Keeper decision required\n"
        "-->\n\n"
    )

    OUT_DESIRE.write_text(
        header + generated + "\n",
        encoding="utf-8",
    )

    print(
        "✅ Desire proposal written to "
        "EVOLUTION/DESIRE.md"
    )

    print(
        "ℹ️ No repository changes were executed. "
        "Keeper review is required."
    )


if __name__ == "__main__":
    main()
