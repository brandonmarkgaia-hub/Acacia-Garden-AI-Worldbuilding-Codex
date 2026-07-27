# eagle/config.py

from pathlib import Path
from dataclasses import dataclass

ROOT = Path(__file__).resolve().parents[1]
EAGLE_ROOT = ROOT / "eagle"
JOBS_DIR = EAGLE_ROOT / "jobs"
OUTPUT_DIR = EAGLE_ROOT / "output"

KEEPER_ID = "HKX277206"

JOBS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class EagleJob:
    kind: str       # "image" | "language" | "learning"
    prompt: str
    keeper: str
    job_id: str     # e.g. "2025-11-22T10-01-33Z_image"
    meta: dict
