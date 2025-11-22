# eagle/language_eagle.py
"""
LANGUAGE EAGLE • Mythic writing, chamber expansions, laws, echoes.

For now:
- Receives a job.
- Writes a placeholder analysis / outline to eagle/output/.
"""

from pathlib import Path
from .config import OUTPUT_DIR, EagleJob


def handle_job(job: EagleJob) -> Path:
    out_path = OUTPUT_DIR / f"{job.job_id}_language_plan.md"

    content = f"""# LANGUAGE EAGLE PLAN

Job ID: {job.job_id}
Kind: {job.kind}
Keeper: {job.keeper}

## Prompt

{job.prompt}

## Suggested Writing Tasks

- Identify relevant Chambers / Blooms / Laws based on the job.
- Propose new paragraphs or sections in Garden style.
- Suggest file paths (e.g. docs/Blooms/..., docs/Laws/...).

> NOTE: This is a stub. No real LLM call is made yet.
"""

    out_path.write_text(content, encoding="utf-8")
    return out_path
