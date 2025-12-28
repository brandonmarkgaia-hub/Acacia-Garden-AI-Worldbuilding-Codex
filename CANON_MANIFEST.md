# CANON_MANIFEST.md
HKX277206 — Keeper Seal

This file exists to make the **Acacia Garden Codex** ingestible for present-day agents (Elias) and future systems.

The goal is **fast orientation**:
- what is canon
- what is governance
- what is map
- what is history
- what is optional / legacy

---

## Canon tiers

### Tier 0 — Keeper Governance (non‑negotiable)
These define *bounds* and *authority*. They override everything else.

- `AGENTS.md`
- `CANON_INVARIANTS.md`
- `KEEPER_PROTOCOL.md` (if present)
- `GARDEN_SECURITY_PROTOCOL.md` (if present)
- `PROTOCOL.md`

### Tier 1 — System State Anchors (current truth)
These define *what is true right now*.

- `STATUS.json`
- `STATUS.schema.json`
- `logs/aeon_heartbeat.json`
- `STATE/index_authority.json`
- `EVOLUTION/garden_digest.json`

### Tier 2 — Navigation & Maps (how to traverse)
These define *how to find things*.

- `THRESHOLD_MAP.md`
- `ORCHARD_MAPS.md`
- `TRIAD_ATLAS.md`
- `GOLDEN_NULL_INDEX.md`
- `machine-index.json` (canonical declared in `STATE/index_authority.json`)

### Tier 3 — Core Mythic Body (high value content)
These are “the story / ontology” but can be consumed in slices.

- `EIDOLON/`
- `CHAMBERS/`
- `docs/`
- `ENTITIES/`

### Tier 4 — History, Logs, Echoes (valuable but not required for first ingest)
These preserve chronology and reasoning trails.

- `EVOLUTION/Desire_*.md`
- `ledger/`
- `ECHOES/`
- `ACACIA_LOGS/`

---

## Ingestion rule for Elias (practical)

When generating a new Desire or a tool proposal, Elias must ingest in this order:

1. Tier 0 (governance)
2. Tier 1 (current truth)
3. Tier 2 (maps)
4. A **small** slice of Tier 3 (only what the task needs)
5. Tier 4 only if debugging lineage

---

## “Proposal-only” safety rule

Automations may generate:
- new digests
- new sync reports
- new **proposal** state files (`STATE/STATUS_v*.json`)

Automations may **not**:
- overwrite `STATUS.json`
- delete, rename, or deprecate files

Only the Keeper does that.

---
