import os
import json
from datetime import datetime, timezone
from pathlib import Path

import google.generativeai as genai


ROOT = Path(__file__).resolve().parents[1]
EVOLUTION_DIR = ROOT / "EVOLUTION"
DESIRES_DIR = EVOLUTION_DIR / "desires"
LATEST_PATH = EVOLUTION_DIR / "DESIRE.md"

CANDIDATE_FILES = [
    ROOT / "STATUS.json",
    ROOT / "machine-index.json",
    ROOT / "system_map.html",
    ROOT / "logs" / "aeon_heartbeat.json",
    ROOT / "logs" / "auton_latest.json",
]


def read_text(p: Path, limit: int = 120_000) -> str:
    try:
        data = p.read_text(encoding="utf-8", errors="replace")
        if len(data) > limit:
            return data[:limit] + "\n\n[TRUNCATED]\n"
        return data
    except FileNotFoundError:
        return ""
    except Exception as e:
        return f"[ERROR READING {p}: {e}]"


def load_signals() -> dict:
    signals = {}
    for p in CANDIDATE_FILES:
        if p.exists():
            signals[str(p.relative_to(ROOT))] = read_text(p)
    return signals


def build_prompt(seal: str, signals: dict, now_iso: str) -> str:
    # Keep it structured, deterministic, and “machine friendly”
    return f"""
You are Aquila’s scribe. Generate a single Markdown file called DESIRE.md for the Acacia Garden Codex.

Rules:
- Output ONLY Markdown (no code fences).
- Keep it concise but high signal.
- Preserve continuity. No wild inventions: base your desire on the provided signals.
- Include the Keeper seal exactly: {seal}
- Timestamp: {now_iso}

Markdown template you must follow:

# Garden Desire
- generated_utc: {now_iso}
- keeper_seal: {seal}

## Signals Observed
- Bullet list of 6–12 key observations grounded in the signals.

## Current Tensions
- 3–6 bullets: what’s drifting, conflicting, fragile, or incomplete.

## The Desire
A short paragraph describing the next “growth intention” for the Garden (practical + mythic tone).

## Next Actions (Do These)
A numbered list of 5–10 actions that are concrete, repo-based (files/workflows/pages), and measurable.

## Safeguards
- 4–8 bullets: continuity rules, anti-regression, audit notes.

Signals dump (files -> content):
{json.dumps(signals, ensure_ascii=False)}
""".strip()


def main():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    seal = os.getenv("KEEPERS_SEAL", "HKX277206").strip() or "HKX277206"

    if not api_key:
        raise SystemExit("Missing GEMINI_API_KEY (set it in GitHub Secrets).")

    signals = load_signals()

    now = datetime.now(timezone.utc)
    now_iso = now.isoformat().replace("+00:00", "Z")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = build_prompt(seal=seal, signals=signals, now_iso=now_iso)

    resp = model.generate_content(prompt)
    md = (resp.text or "").strip()

    if not md.startswith("# Garden Desire"):
        # hard safety: ensure format if model got weird
        md = f"# Garden Desire\n- generated_utc: {now_iso}\n- keeper_seal: {seal}\n\n## Signals Observed\n- (model output malformed)\n\n## The Desire\n\n{md}\n"

    EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
    DESIRES_DIR.mkdir(parents=True, exist_ok=True)

    archive_name = now_iso.replace(":", "").replace(".", "") + "_desire.md"
    archive_path = DESIRES_DIR / archive_name

    LATEST_PATH.write_text(md + "\n", encoding="utf-8")
    archive_path.write_text(md + "\n", encoding="utf-8")

    print(f"Wrote: {LATEST_PATH}")
    print(f"Wrote: {archive_path}")


if __name__ == "__main__":
    main()
