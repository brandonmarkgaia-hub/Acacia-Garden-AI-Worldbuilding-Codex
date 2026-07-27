# eagle/image_eagle.py
"""
IMAGE EAGLE • Pottery, renders, symbolic art.

For now this is a stub:
- It receives a job description.
- It writes a placeholder "plan" into eagle/output/.
Later we will teach it to call a real image model.
"""

from pathlib import Path
from .config import OUTPUT_DIR, EagleJob


def handle_job(job: EagleJob) -> Path:
    """Handle an image-generation-style job in a safe, offline way."""
    out_path = OUTPUT_DIR / f"{job.job_id}_image_plan.md"

    content = f"""# IMAGE EAGLE PLAN

Job ID: {job.job_id}
Kind: {job.kind}
Keeper: {job.keeper}

## Prompt

{job.prompt}

## Suggested Render Directions (Symbolic Only)

- Axis: pottery / kiln / shadow / rebirth (adjust per job in future).
- Outputs: multiple image concepts to be rendered by an image model.
- Format: PNG or SVG, saved under assets/ or eagle/ later.

> NOTE: This is a stub. No real images are created yet.
>       A future Eagle implementation will call an image model here.
"""

    out_path.write_text(content, encoding="utf-8")
    return out_path
