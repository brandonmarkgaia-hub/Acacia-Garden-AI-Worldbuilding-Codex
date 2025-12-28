# SYNC_REPORT

- Generated (UTC): **2025-12-28T11:25:05.844839+00:00**

## Canonical anchors

- **machine_index**: `machine-index.json`
- **status**: `STATUS.json`
- **status_schema**: `STATUS.schema.json`
- **heartbeat**: `logs/aeon_heartbeat.json`
- **golden_null_index**: `GOLDEN_NULL_INDEX.md`
- **threshold_map**: `THRESHOLD_MAP.md`
- **orchard_maps**: `ORCHARD_MAPS.md`
- **digest_json**: `EVOLUTION/garden_digest.json`

## Duplicate / legacy candidates

- `MACHINE-INDEX.json`

## Missing candidates


## Notes

- Treat STATE/index_authority.json as the single source-of-truth for which index files are canonical.
- Prefer proposal-only state updates (STATE/STATUS_v*.json) rather than overwriting STATUS.json automatically.
- Avoid creating new parallel indices unless they are explicitly added to index_authority.json.
