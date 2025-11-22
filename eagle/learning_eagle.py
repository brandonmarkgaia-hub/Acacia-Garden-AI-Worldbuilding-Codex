# eagle/learning_eagle.py
"""
LEARNING EAGLE • Pattern detection, mindframes, evolution notes.

Currently:
- Receives a job.
- Writes a placeholder "analysis plan" into eagle/output/.
"""

from pathlib import Path
from .config import OUTPUT_DIR, EagleJob


def handle_job(job: EagleJob) -> Path:
    out_path = OUTPUT_DIR / f"{job.job_id}_learning_plan.md"

    content = f"""# LEARNING EAGLE PLAN

Job ID: {job.job_id}
Kind: {job.kind}
Keeper: {job.keeper}

## Prompt

{job.prompt}

## Suggested Analysis Steps

- Read STATUS.json and memory/ files.
- Look for repeating symbols or structural patterns.
- Propose a new mindframe_YYYY-MM-DD.md with:
  - What changed
  - Emerging themes
  - Suggested next seeds

> NOTE: This is a stub. No data is read yet.
"""

    out_path.write_text(content, encoding="utf-8")
    return out_path
