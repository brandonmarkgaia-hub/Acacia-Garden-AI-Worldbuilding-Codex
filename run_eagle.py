#!/usr/bin/env python

"""
RUN EAGLE • HKX277206

- Reads the latest JSON job in eagle/jobs/
- Builds an EagleJob
- Dispatches to the Eagle core
- Writes output into eagle/output/
"""

import json
from pathlib import Path

from eagle.config import KEEPER_ID, EagleJob
from eagle.runner import run_job


ROOT = Path(__file__).resolve().parent
JOBS_DIR = ROOT / "eagle" / "jobs"


def load_latest_job() -> EagleJob | None:
    jobs = sorted(JOBS_DIR.glob("*.json"))
    if not jobs:
        print("[EAGLE] No jobs found in eagle/jobs/")
        return None

    latest = max(jobs, key=lambda p: p.stat().st_mtime)
    data = json.loads(latest.read_text(encoding="utf-8"))

    kind = (data.get("kind") or data.get("type") or "language").lower()
    prompt = data.get("prompt", "").strip() or "(no prompt provided)"

    meta = {k: v for k, v in data.items() if k not in ("kind", "type", "prompt")}

    job_id = latest.stem

    print(f"[EAGLE] Loaded job: {latest.name}")
    print(f"[EAGLE] Kind  : {kind}")
    print(f"[EAGLE] Prompt: {prompt[:80]}...")

    return EagleJob(
        kind=kind,
        prompt=prompt,
        keeper=KEEPER_ID,
        job_id=job_id,
        meta=meta,
    )


def main() -> int:
    job = load_latest_job()
    if job is None:
        return 0

    out_path = run_job(job)
    rel = out_path.relative_to(ROOT)
    print(f"[EAGLE] Output written to: {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
