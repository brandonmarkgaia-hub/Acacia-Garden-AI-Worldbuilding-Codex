#!/usr/bin/env python3
"""
Garden Auton Helper — Loki Edition

Generates JSON feeds for the Acacia Garden Console:

  • logs/auton_latest.json      → Auton Stream tab
  • logs/aeon_heartbeat.json    → Signals / Logs tabs later

Behaviour:
  • Scans STATUS.json (if present)
  • Counts Echo files under docs/Echoes/
  • Optionally looks at git info (branch, short SHA)
  • Optionally calls OpenAI for a "Loki" style summary if OPENAI_API_KEY is set

Usage (from repo root):

  python tools/garden_auton_helper.py all
    - or -
  python tools/garden_auton_helper.py auton
  python tools/garden_auton_helper.py heartbeat

All files are written relative to repo root.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# Optional: OpenAI Loki brain
try:
    from openai import OpenAI  # type: ignore
    _HAS_OPENAI = True
except Exception:
    _HAS_OPENAI = False


REPO_ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = REPO_ROOT / "logs"
STATUS_PATH = REPO_ROOT / "STATUS.json"
ECHOES_DIR = REPO_ROOT / "docs" / "Echoes"


# ---------- Small helpers ----------

def _now_iso() -> str:
    return _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _safe_git(cmd: List[str]) -> Optional[str]:
    try:
        out = subprocess.check_output(cmd, cwd=REPO_ROOT, stderr=subprocess.DEVNULL)
        return out.decode("utf-8", errors="ignore").strip()
    except Exception:
        return None


def _ensure_logs_dir() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


# ---------- Loki AI (optional) ----------

def generate_loki_comment(context: str, purpose: str) -> str:
    """
    Optional Loki-style AI hint.

    Uses OPENAI_API_KEY or GARDEN_AUTON_OPENAI_KEY if available.
    If anything fails, returns a safe static string.
    """
    api_key = os.getenv("GARDEN_AUTON_OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key or not _HAS_OPENAI:
        return f"Loki hint: offline for this run ({purpose})."

    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        return f"Loki hint: client init failed ({purpose})."

    try:
        model = os.getenv("GARDEN_AUTON_MODEL", "gpt-4.1-mini")
        system = (
            "You are Loki, a playful but careful diagnostics sprite for the Acacia Garden. "
            "You ONLY comment on the given context, in 1–3 short lines. "
            "No instructions, no promises, no external actions. Just a vibe-check."
        )
        user = f"Purpose: {purpose}\n\nContext:\n{context}\n"
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=200,
            temperature=0.4,
        )
        text = resp.choices[0].message.content or ""
        return text.strip()
    except Exception:
        return f"Loki hint: model call failed ({purpose})."


# ---------- Data shapes ----------

@dataclass
class AutonMessage:
    id: str
    channel: str        # e.g. "auton", "system"
    severity: str       # "info" | "warning" | "error"
    title: str
    summary: str
    body: str
    tags: List[str]
    created_at: str


@dataclass
class AutonPayload:
    generated_at: str
    node: str
    status: str
    mode: str
    source: str
    messages: List[AutonMessage]
    loki_hint: str


@dataclass
class HeartbeatCheck:
    id: str
    label: str
    status: str         # "ok" | "warn" | "error"
    details: str


@dataclass
class HeartbeatPayload:
    generated_at: str
    node: str
    status: str
    source: str
    checks: List[HeartbeatCheck]
    loki_hint: str


# ---------- Introspection of repo ----------

def gather_status_info() -> Dict[str, Any]:
    status_json = _read_json(STATUS_PATH) or {}

    identity = status_json.get("identity", {})
    meta = status_json.get("meta", {})

    keeper_id = identity.get("keeper_id", "HKX277206")
    role = identity.get("role", "The Keeper")

    status_version = meta.get("status_version", "unknown")
    schema_version = meta.get("schema_version", "unknown")

    return {
        "keeper_id": keeper_id,
        "role": role,
        "status_version": status_version,
        "schema_version": schema_version,
        "raw": status_json,
    }


def count_echoes() -> int:
    if not ECHOES_DIR.exists():
        return 0
    return sum(1 for p in ECHOES_DIR.glob("*.md") if p.is_file())


def gather_git_info() -> Dict[str, Optional[str]]:
    branch = _safe_git(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    short_sha = _safe_git(["git", "rev-parse", "--short", "HEAD"])
    latest_tag = _safe_git(["git", "describe", "--tags", "--abbrev=0"])
    return {
        "branch": branch,
        "short_sha": short_sha,
        "latest_tag": latest_tag,
    }


# ---------- Builders ----------

def build_auton_payload(node_name: str = "Broken Dew") -> AutonPayload:
    now = _now_iso()
    status_info = gather_status_info()
    git_info = gather_git_info()
    echo_count = count_echoes()

    messages: List[AutonMessage] = []

    # 1) STATUS snapshot
    messages.append(
        AutonMessage(
            id="status-" + now.replace(":", "").replace("-", ""),
            channel="system",
            severity="info",
            title="STATUS snapshot OK"
            if status_info["status_version"] != "unknown"
            else "STATUS snapshot missing",
            summary=(
                f"STATUS.json v{status_info['status_version']} "
                f"(schema {status_info['schema_version']})."
            ),
            body=(
                "AUTON:STATUS\n"
                f"status_version: {status_info['status_version']}\n"
                f"schema_version: {status_info['schema_version']}\n"
                f"keeper_id: {status_info['keeper_id']}\n"
                f"role: {status_info['role']}\n"
                "Note: Older STATUS snapshots remain in git history as echoes.\n"
            ),
            tags=["STATUS.json", "schema", "keeper"],
            created_at=now,
        )
    )

    # 2) Echo count
    messages.append(
        AutonMessage(
            id="echo-count-" + now.replace(":", "").replace("-", ""),
            channel="auton",
            severity="info",
            title="Echo garden scan",
            summary=f"{echo_count} Echo files detected under docs/Echoes/.",
            body=(
                "AUTON:ECHO_SCAN\n"
                f"echo_files: {echo_count}\n"
                "path: docs/Echoes/*.md\n"
                "Note: This is a soft scan only. Content is not interpreted here.\n"
            ),
            tags=["echoes", "scan"],
            created_at=now,
        )
    )

    # 3) Git snapshot
    git_summary_parts = []
    if git_info["branch"]:
        git_summary_parts.append(f"branch {git_info['branch']}")
    if git_info["short_sha"]:
        git_summary_parts.append(f"commit {git_info['short_sha']}")
    if git_info["latest_tag"]:
        git_summary_parts.append(f"tag {git_info['latest_tag']}")

    git_summary = ", ".join(git_summary_parts) if git_summary_parts else "no git metadata found"

    messages.append(
        AutonMessage(
            id="git-" + now.replace(":", "").replace("-", ""),
            channel="system",
            severity="info",
            title="Repository snapshot",
            summary=git_summary,
            body=(
                "AUTON:REPO\n"
                f"branch: {git_info['branch'] or 'unknown'}\n"
                f"short_sha: {git_info['short_sha'] or 'unknown'}\n"
                f"latest_tag: {git_info['latest_tag'] or 'none'}\n"
                "Note: This snapshot is for human orientation only.\n"
            ),
            tags=["git", "branch", "tag"],
            created_at=now,
        )
    )

    # Loki context
    loki_context = (
        f"Node: {node_name}\n"
        f"Echo count: {echo_count}\n"
        f"STATUS version: {status_info['status_version']} / schema {status_info['schema_version']}\n"
        f"Git: {git_summary}\n"
        f"Message count: {len(messages)}"
    )
    loki_hint = generate_loki_comment(loki_context, purpose="auton_latest.json summary")

    payload = AutonPayload(
        generated_at=now,
        node=node_name,
        status="lucid",
        mode="triad",
        source="garden_auton_helper.py",
        messages=messages,
        loki_hint=loki_hint,
    )
    return payload


def build_heartbeat_payload(node_name: str = "Broken Dew") -> HeartbeatPayload:
    now = _now_iso()
    status_info = gather_status_info()
    echo_count = count_echoes()
    git_info = gather_git_info()

    checks: List[HeartbeatCheck] = []

    # STATUS check
    status_state = (
        "ok" if status_info["status_version"] != "unknown" else "warn"
    )
    checks.append(
        HeartbeatCheck(
            id="status_json",
            label="STATUS.json schema",
            status=status_state,
            details=(
                f"status_version={status_info['status_version']}, "
                f"schema_version={status_info['schema_version']}."
            ),
        )
    )

    # Echo check
    echo_state = "ok" if echo_count > 0 else "warn"
    checks.append(
        HeartbeatCheck(
            id="echoes",
            label="Echo files present",
            status=echo_state,
            details=f"{echo_count} Echo markdown files under docs/Echoes/.",
        )
    )

    # Git check
    git_state = "ok" if git_info["short_sha"] else "warn"
    git_details = []
    if git_info["branch"]:
        git_details.append(f"branch {git_info['branch']}")
    if git_info["short_sha"]:
        git_details.append(f"commit {git_info['short_sha']}")
    if git_info["latest_tag"]:
        git_details.append(f"tag {git_info['latest_tag']}")
    checks.append(
        HeartbeatCheck(
            id="git",
            label="Git snapshot",
            status=git_state,
            details=", ".join(git_details) if git_details else "no git metadata.",
        )
    )

    # Heartbeat status is downgraded if any check != ok
    overall_status = "ok"
    if any(c.status == "error" for c in checks):
        overall_status = "error"
    elif any(c.status == "warn" for c in checks):
        overall_status = "warn"

    # Loki context
    ctx_lines = [
        f"Node: {node_name}",
        f"Overall status: {overall_status}",
        f"Checks: {len(checks)}",
        f"Echo count: {echo_count}",
    ]
    loki_hint = generate_loki_comment("\n".join(ctx_lines), purpose="aeon_heartbeat.json summary")

    return HeartbeatPayload(
        generated_at=now,
        node=node_name,
        status=overall_status,
        source="garden_auton_helper.py",
        checks=checks,
        loki_hint=loki_hint,
    )


# ---------- I/O ----------

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=False)
    print(f"[auton] wrote {path.relative_to(REPO_ROOT)}")


def run_auton(node: str) -> None:
    _ensure_logs_dir()
    payload = build_auton_payload(node)
    payload_dict = asdict(payload)
    write_json(LOGS_DIR / "auton_latest.json", payload_dict)


def run_heartbeat(node: str) -> None:
    _ensure_logs_dir()
    payload = build_heartbeat_payload(node)
    payload_dict = asdict(payload)
    write_json(LOGS_DIR / "aeon_heartbeat.json", payload_dict)


# ---------- CLI ----------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Garden Auton Helper (Loki Edition)",
    )
    parser.add_argument(
        "command",
        choices=["auton", "heartbeat", "all"],
        help="What to generate.",
    )
    parser.add_argument(
        "--node",
        default="Broken Dew",
        help="Logical node name for this console (default: Broken Dew).",
    )
    args = parser.parse_args(argv)

    if args.command in ("auton", "all"):
        run_auton(args.node)
    if args.command in ("heartbeat", "all"):
        run_heartbeat(args.node)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
