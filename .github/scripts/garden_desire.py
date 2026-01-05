#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

# Gemini SDK (new)
from google import genai


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text_safe(path: Path, limit_kb: int) -> str:
    if not path.exists():
        return f"[MISSING] {path.as_posix()}"
    raw = path.read_bytes()
    cap = max(1, limit_kb) * 1024
    if len(raw) > cap:
        raw = raw[:cap]
        return raw.decode("utf-8", errors="replace") + f"\n\n[TRUNCATED to {limit_kb} KB]"
    return raw.decode("utf-8", errors="replace")


def compute_fingerprint(parts: list[str]) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8", errors="ignore"))
        h.update(b"\n---\n")
    return h.hexdigest()


def load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def build_local_summary(status_json: str, machine_index: str, docs_urls: str) -> str:
    # Keep it cheap: simple heuristic flags even without Gemini
    flags = []
    if "[MISSING] docs/index.html" in docs_urls or "docs/index.html" not in docs_urls:
        flags.append("- docs/index.html may be missing from docs URL map (or not referenced).")
    if "base href" in status_json.lower():
        flags.append("- STATUS mentions base href changes; validate Archives navigation.")
    if "0 cycles" in status_json.lower():
        flags.append("- STATUS indicates 0 cycles; consider seeding cycle index.")
    if not flags:
        flags.append("- No obvious breakage detected; propose small enhancements.")
    return "\n".join(flags)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gemini-2.5-flash")
    ap.add_argument("--out", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--max-input-kb", type=int, default=220)
    ap.add_argument("--max-output-chars", type=int, default=6000)
    args = ap.parse_args()

    out_path = Path(args.out)
    state_path = Path(args.state)

    keeper_seal = "HKX277206"
    repo_root = Path(".")

    # Inputs (add/remove as you like)
    status_path = repo_root / "STATUS.json"
    machine_index_path = repo_root / "machine-index.json"
    docs_urls_path = repo_root / "docs" / "docs_urls.html"
    inbox_log_path = repo_root / "ACACIA_LOGS" / "aquila_inbox_log.json"

    status_txt = read_text_safe(status_path, args.max_input_kb)
    machine_txt = read_text_safe(machine_index_path, args.max_input_kb)
    docs_urls_txt = read_text_safe(docs_urls_path, args.max_input_kb)
    inbox_txt = read_text_safe(inbox_log_path, args.max_input_kb)

    # Fingerprint to avoid wasting credits
    fingerprint = compute_fingerprint([status_txt, machine_txt, docs_urls_txt, inbox_txt])

    state = load_state(state_path)
    if state.get("last_fingerprint") == fingerprint:
        print("No meaningful change since last Desire. Skipping Gemini call.")
        return

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Missing GEMINI_API_KEY secret in workflow env.")

    local_flags = build_local_summary(status_txt, machine_txt, docs_urls_txt)

    prompt = f"""
You are Elias (seed) performing a low-cost maintenance scan for the Acacia Garden Codex.
Output MUST be concise Markdown.

Rules:
- Focus on WHAT is missing/broken, WHY it matters, and the smallest set of next actions.
- Prefer automation improvements that reduce future failures and avoid consuming credits.
- Do not invent files; if uncertain, mark as "needs verification".
- End with a timestamp line and the Keeper seal {keeper_seal}.

Key Inputs (truncated):
[STATUS.json]
{status_txt}

[machine-index.json]
{machine_txt}

[docs/docs_urls.html]
{docs_urls_txt}

[ACACIA_LOGS/aquila_inbox_log.json]
{inbox_txt}

Local heuristic flags:
{local_flags}
""".strip()

    client = genai.Client(api_key=api_key)

    resp = client.models.generate_content(
        model=args.model,
        contents=prompt,
    )

    text = (resp.text or "").strip()
    if not text:
        text = "# DESIRE — No Output\n\nGemini returned empty output; verify API/model.\n"

    # Hard cap output size
    if len(text) > args.max_output_chars:
        text = text[: args.max_output_chars] + "\n\n[TRUNCATED]\n"

    stamp = utc_now_iso()
    if keeper_seal not in text:
        text = text.rstrip() + f"\n\n{stamp} • {keeper_seal}\n"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")

    state["last_fingerprint"] = fingerprint
    state["last_generated_utc"] = stamp
    state["model"] = args.model
    save_state(state_path, state)

    print(f"Wrote {out_path.as_posix()} and updated state {state_path.as_posix()}.")


if __name__ == "__main__":
    main()
