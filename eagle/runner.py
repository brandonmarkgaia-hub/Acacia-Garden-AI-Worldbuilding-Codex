# eagle/runner.py
"""
EAGLE RUNNER CORE

Responsible for:
- Creating a job structure
- Writing the job JSON to eagle/jobs/
- Dispatching to the correct Eagle handler (image/language/learning)

No external LLMs are called yet.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from .config import JOBS_DIR, EagleJob, KEEPER_ID
from . import image_eagle, language_eagle, learning_eagle


EagleKind = Literal["image", "language", "learning"]


def _iso_job_id(kind: str) -> str:
    now = datetime.now(timezone.utc)
    iso = now.strftime("%Y-%m-%dT%H-%M-%SZ")
    return f"{iso}_{kind}"


def create_job(kind: EagleKind, prompt: str, meta: dict | None = None) -> EagleJob:
    job_id = _iso_job_id(kind)
    job = EagleJob(
        kind=kind,
        prompt=prompt,
        keeper=KEEPER_ID,
        job_id=job_id,
        meta=meta or {},
    )

    job_path = JOBS_DIR / f"{job_id}.json"
    job_payload = {
        "job_id": job.job_id,
        "kind": job.kind,
        "keeper": job.keeper,
        "prompt": job.prompt,
        "meta": job.meta,
    }
    job_path.write_text(json.dumps(job_payload, indent=2), encoding="utf-8")
    return job


def run_job(job: EagleJob) -> Path:
    if job.kind == "image":
        return image_eagle.handle_job(job)
    if job.kind == "language":
        return language_eagle.handle_job(job)
    if job.kind == "learning":
        return learning_eagle.handle_job(job)
    raise ValueError(f"Unknown Eagle kind: {job.kind}")
