# Verified audit artifact triage — 2026-10-24

**Status:** evidence register, not Canon; no checksum or historical source rewrite.

Source: GitHub Actions run [39846567770](https://github.com/brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex/actions/runs/39846567770), artifact [12455228351](https://github.com/brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex/actions/runs/39846567770/artifacts/12455228351), `corpus-integrity.json`. The findings are checkout-relative and may change on later commits.

## All 10 mismatched checksum paths

- `STATUS.json`
- `docs/Chambers/chambers_index.json`
- `docs/Chambers/index.html`
- `docs/Echoes/echoes_index.json`
- `docs/Echoes/index.html`
- `docs/GardenOS/index.html`
- `docs/Novellas/garden_index.json`
- `docs/Vaults/index.html`
- `docs/docs_urls.json`
- `machine-index.json`

These include several generated-looking indexes, but that is **not** proof of the cause. Preserve the expected hashes and investigate their generation history before any checksum refresh. There were zero missing checksum paths in the audit.

## All 78 simple Markdown link findings, grouped by source

| Source | Findings | Triage |
| --- | ---: | --- |
| `_ROOT_ARCHIVE/md/garden_scan_report.md` | 37 | Archived scan report; relative references point outside its actual source directory; duplicates and an ellipsis occur; preserve archival evidence |
| `docs/ACACIA_SPECS/ARCHETYPE_PROMPT_SCHEMA.md` | 3 | Examples use uppercase placeholder paths; inspect before treating as navigational links |
| `docs/Cycles/003_ECHO_HKX277206_ACACIA.md` | 3 | `../explorer.html` and `../cycle-index.html` do not resolve in checkout; corresponding files exist at repository root |
| `docs/Cycles/003_ECHO_HKX277206_FLEET_RETURN_SIGNAL.md` | 3 | Same root-relative path mismatch |
| `docs/Cycles/004_ECHO_HKX277206_ORACLE_BREATH.md` | 3 | Same root-relative path mismatch |
| `docs/Cycles/004_ECHO_HKX277206_ROOT.md` | 3 | Same root-relative path mismatch |
| `docs/Cycles/005_ECHO_HKX277206_ARCHIVE_VEIN.md` | 3 | Same root-relative path mismatch |
| `docs/Cycles/005_ECHO_HKX277206_GENESIS_GAIA.md` | 3 | Same root-relative path mismatch |
| `docs/Cycles/006_ECHO_HKX277206_REMEMBRANCE.md` | 2 | Same root-relative path mismatch |
| `docs/Cycles/007_ECHO_HKX277206_SEED_VAULT_MATRIX.md` | 2 | Same root-relative path mismatch |
| `docs/Novellas/BOOK_OF_THE_EVENTIDE_LEDGER.md` | 1 | Echo issue reference requires target review |
| `docs/dashboard.md` | 7 | Uppercase folder names and `../` paths do not match checkout; review intended targets |
| `docs/library.md` | 1 | `../LIBRARY/` is wrong case and location; `docs/Library/BOOK_SUMMARY_INDEX.md` exists |
| `docs/sidebar.md` | 7 | One named missing novella and six ellipsis placeholders; do not invent content |

Counts: 37+3+3+3+3+3+3+3+2+2+1+7+1+7 = **78**.

## Verified conservative repair candidates

The eight `docs/Cycles/` files collectively contain **22** links to root-level `explorer.html` or `cycle-index.html` using one too few `../` segments. A mechanical repair to `../../explorer.html` and `../../cycle-index.html` can be verified against the actual repository tree; keep fragment identifiers unchanged. `docs/library.md` can point to `Library/BOOK_SUMMARY_INDEX.md` relative to `docs/`. Do not infer fixes for archived reports, placeholders, or the other links without independent target confirmation.

## Open items

- The ten checksum mismatches still require per-file expected/current digest and commit-history analysis.
- The remaining link findings require source-specific review; a syntactic link check does not model all site routing.
- 1,384 unknown authority classifications remain unknown. No AI bulk Law promotion.
- The Keeper's independent Ed25519 signature and key-to-identity binding are not supplied; no cryptographic authentication claimed.
