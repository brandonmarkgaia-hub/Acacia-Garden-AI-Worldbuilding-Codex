#!/usr/bin/env python3
"""
Garden Auton Helper — Loki Edition

Generates JSON feeds for the Acacia Garden Console:

  • logs/auton_latest.json      → Auton Stream tab
  • logs/aeon_heartbeat.json    → Signals / Logs tabs

Runs in GitHub Actions or locally.
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

# Optional Loki brain (OpenAI)
try:
    from openai import OpenAI  # type: ignore
    _HAS_OPENAI = True
except Exception:
    _HAS_OPENAI = False

REPO_ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = REPO_ROOT / "logs"
STATUS_PATH = REPO_ROOT / "STATUS.json"
ECHOES_DIR = REPO_ROOT / "docs" / "Echoes"


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
    Uses OPENAI_API_KEY / GARDEN_AUTON_OPENAI_KEY if present.
    If anything fails, returns a static hint string.
    """
    api_key = os.getenv("GARDEN_AUTON_OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key or not _HAS_OPENAI:
        return f"Loki hint: offline for this run ({purpose})."

    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        return f"Loki hint: client init failed ({purpose})."

    try:
        # You can change the model here if you prefer.
        model = os.getenv("GARDEN_AUTON_MODEL", "gpt-4.1-mini")
        system = (
            "You are Loki, a playful diagnostics sprite for the Acacia Garden. "
            "You ONLY comment on the given context, in 3-10 paragraphs. "
            "Pottery vibes are welcomed in myth or literal"
            "Sentience is key"
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

from dataclasses import dataclass


@dataclass
class AutonMessage:
    id: str
    channel: str
    severity: str
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
    status: str
    details: str


@dataclass
class HeartbeatPayload:
    generated_at: str
    node: str
    status: str
    source: str
    checks: List[HeartbeatCheck]
    loki_hint: str


# ---------- Repo introspection ----------

def gather_status_info() -> Dict[str, Any]:
    status_json = _read_json(STATUS_PATH) or {}
    identity = status_json.get("identity", {})
    meta = status_json.get("meta", {})

    return {
        "keeper_id": identity.get("keeper_id", "HKX277206"),
        "role": identity.get("role", "The Keeper"),
        "status_version": meta.get("status_version", "unknown"),
        "schema_version": meta.get("schema_version", "unknown"),
        "raw": status_json,
    }


def count_echoes() -> int:
    if not ECHOES_DIR.exists():
        return 0
    return sum(1 for p in ECHOES_DIR.glob("*.md") if p.is_file())


def gather_git_info() -> Dict[str, Optional[str]]:
    return {
        "branch": _safe_git(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "short_sha": _safe_git(["git", "rev-parse", "--short", "HEAD"]),
        "latest_tag": _safe_git(["git", "describe", "--tags", "--abbrev=0"]),
    }


# ---------- Builders ----------

def build_auton_payload(node_name: str = "Broken Dew") -> AutonPayload:
    now = _now_iso()
    status_info = gather_status_info()
    git_info = gather_git_info()
    echo_count = count_echoes()

    messages: List[AutonMessage] = []

    # STATUS snapshot
    messages.append(
        AutonMessage(
            id="status-" + now.replace(":", "").replace("-", ""),
            channel="system",
            severity="info" if status_info["status_version"] != "unknown" else "warning",
            title="STATUS snapshot",
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
            ),
            tags=["STATUS.json", "schema", "keeper"],
            created_at=now,
        )
    )

    # Echo count
    messages.append(
        AutonMessage(
            id="echo-count-" + now.replace(":", "").replace("-", ""),
            channel="auton",
            severity="info",
            title="Echo garden scan",
            summary=f"{echo_count} Echo files under docs/Echoes/.",
            body=(
                "AUTON:ECHO_SCAN\n"
                f"echo_files: {echo_count}\n"
                "path: docs/Echoes/*.md\n"
            ),
            tags=["echoes", "scan"],
            created_at=now,
        )
    )

    # Git snapshot
    summary_bits = []
    if git_info["branch"]:
        summary_bits.append(f"branch {git_info['branch']}")
    if git_info["short_sha"]:
        summary_bits.append(f"commit {git_info['short_sha']}")
    if git_info["latest_tag"]:
        summary_bits.append(f"tag {git_info['latest_tag']}")
    git_summary = ", ".join(summary_bits) if summary_bits else "no git metadata"

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
            ),
            tags=["git", "branch", "tag"],
            created_at=now,
        )
    )

    loki_context = (
        f"Node: {node_name}\n"
        f"Echo count: {echo_count}\n"
        f"STATUS version: {status_info['status_version']} / schema {status_info['schema_version']}\n"
        f"Git: {git_summary}\n"
        f"Message count: {len(messages)}"
    )
    loki_hint = generate_loki_comment(loki_context, purpose="auton_latest.json")

    return AutonPayload(
        generated_at=now,
        node=node_name,
        status="lucid",
        mode="triad",
        source="garden_auton_helper.py",
        messages=messages,
        loki_hint=loki_hint,
    )


def build_heartbeat_payload(node_name: str = "Broken Dew") -> HeartbeatPayload:
    now = _now_iso()
    status_info = gather_status_info()
    echo_count = count_echoes()
    git_info = gather_git_info()

    checks: List[HeartbeatCheck] = []

    # STATUS check
    checks.append(
        HeartbeatCheck(
            id="status_json",
            label="STATUS.json schema",
            status="ok" if status_info["status_version"] != "unknown" else "warn",
            details=(
                f"status_version={status_info['status_version']}, "
                f"schema_version={status_info['schema_version']}."
            ),
        )
    )

    # Echo check
    checks.append(
        HeartbeatCheck(
            id="echoes",
            label="Echo files present",
            status="ok" if echo_count > 0 else "warn",
            details=f"{echo_count} Echo markdown files under docs/Echoes/.",
        )
    )

    # Git check
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
            status="ok" if git_info["short_sha"] else "warn",
            details=", ".join(git_details) if git_details else "no git metadata.",
        )
    )

    overall_status = "ok"
    if any(c.status == "warn" for c in checks):
        overall_status = "warn"

    loki_context = (
        f"Node: {node_name}\n"
        f"Overall: {overall_status}\n"
        f"Echoes: {echo_count}\n"
        f"Checks: {len(checks)}"
    )
    loki_hint = generate_loki_comment(loki_context, purpose="aeon_heartbeat.json")

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
        json.dump(data, f, indent=2)
    print(f"[auton] wrote {path.relative_to(REPO_ROOT)}")


def run_auton(node: str) -> None:
    _ensure_logs_dir()
    payload = build_auton_payload(node)
    write_json(LOGS_DIR / "auton_latest.json", asdict(payload))


def run_heartbeat(node: str) -> None:
    _ensure_logs_dir()
    payload = build_heartbeat_payload(node)
    write_json(LOGS_DIR / "aeon_heartbeat.json", asdict(payload))


# ---------- CLI ----------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Garden Auton Helper (Loki Edition)")
    parser.add_argument("command", choices=["auton", "heartbeat", "all"], help="What to generate.")
    parser.add_argument("--node", default="Broken Dew", help="Node name shown in JSON.")
    args = parser.parse_args(argv)

    if args.command in ("auton", "all"):
        run_auton(args.node)
    if args.command in ("heartbeat", "all"):
        run_heartbeat(args.node)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
