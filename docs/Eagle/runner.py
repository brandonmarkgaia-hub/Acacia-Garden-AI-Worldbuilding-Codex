"""
EAGLE RUNNER • HKX277206

Routes Eagle jobs to the correct module based on kind.
Currently supports: language

This is intentionally simple so we can plug in image / learning later.
"""

from pathlib import Path

from .config import EagleJob
from . import language_eagle


def run_job(job: EagleJob) -> Path:
    kind = (job.kind or "language").lower()

    if kind == "language":
        return language_eagle.run_language(job)

    # Fallback: treat unknown kinds as language for now
    return language_eagle.run_language(job)
