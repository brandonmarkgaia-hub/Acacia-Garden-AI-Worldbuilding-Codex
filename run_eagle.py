#!/usr/bin/env python
"""
RUN EAGLE • CLI entrypoint

Usage examples (from repo root):

  python run_eagle.py image "Generate concepts for kiln pottery around Bloom axis"
  python run_eagle.py language "Draft an outline for Chamber XI text"
  python run_eagle.py learning "Summarise recent Garden evolution"

This does NOT call any real LLMs yet.
It just:
- logs a job in eagle/jobs/
- creates a stub plan in eagle/output/
"""

import sys
from pathlib import Path

from eagle.runner import create_job, run_job


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("Usage: python run_eagle.py <kind> <prompt>")
        print("  kind: image | language | learning")
        return 1

    kind = argv[1].strip().lower()
    prompt = " ".join(argv[2:]).strip()

    if kind not in ("image", "language", "learning"):
        print("Error: kind must be one of: image, language, learning")
        return 1

    job = create_job(kind=kind, prompt=prompt)
    out_path = run_job(job)

    rel_out = Path(out_path).relative_to(Path(__file__).resolve().parent)
    print(f"[EAGLE] Job created: {job.job_id}")
    print(f"[EAGLE] Output written to: {rel_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
