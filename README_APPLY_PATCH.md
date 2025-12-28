# Acacia Elias Patch — Apply Instructions

This bundle adds a **high-signal ingestion spine** for Elias (Gemini workflow) and future agents.

## Files added/updated

- `CANON_MANIFEST.md` (new)
- `tools/garden_digest.py` (new)
- `tools/sync_maestro.py` (new)
- `tools/rcs.py` (new)
- `.github/scripts/garden_evolution.py` (updated / repaired)
- `.github/workflows/garden_evolution.yml` (updated / repaired)

## How to apply

1. Copy the bundle contents into your repo root **preserving paths**.
2. Commit and push.
3. Ensure your repo has the secret: `GEMINI_API_KEY`
4. Trigger: Actions → **Garden Evolution (Elias + Digest + RCS)** → Run workflow

## What you will see after first run

- `EVOLUTION/garden_digest.json` and `.md`
- `STATE/index_authority.json`
- `ACACIA_LOGS/sync_report_YYYYMMDD.md`
- `EVOLUTION/Desire_YYYYMMDD.md` and `.json`
- `STATE/STATUS_vYYYYMMDD_HHMM.json` (proposal-only)
- `STATE/cadence_anchors.json` (append-only log)
- `GOLDEN_NULL_INDEX.md` appended with a cadence proposal line (if file exists)

## Safety model

Nothing deletes or overwrites canon.
All state changes are **proposal-only**.

Keeper decides what becomes `STATUS.json`.
