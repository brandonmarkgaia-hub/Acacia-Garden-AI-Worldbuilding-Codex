# Legacy audit: evidence-specific triage — 2026-10-24

**Status:** advisory technical evidence; no retroactive Keeper seal or automatic authority.

Source: GitHub Actions [run 39846567770](https://github.com/brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex/actions/runs/39846567770), artifact `corpus-integrity-inventory`, checkout `8ad2326e1183a5958d5ee614327ddae606ab7c7c`. Findings describe that checkout, not necessarily current main.

## Exact ten SHA-256 mismatches

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

Most paths *look* generated or machine-managed, but that is a hypothesis, not proof of why hashes differ. Keep the original CHECKSUMS.sha256 intact until per-path history and producer are checked. A passing audit only means the report ran.

## Missing-link grouping

The 78 occurrences are not 78 independently broken destinations:
- 37 occurrences in archived `_ROOT_ARCHIVE/md/garden_scan_report.md` (14 distinct target strings), including literal ellipsis and archived relative paths. Historical snapshot should not be silently rewritten.
- 3 in `docs/ACACIA_SPECS/ARCHETYPE_PROMPT_SCHEMA.md` (3 targets).
- 25 in eight `docs/Cycles/` documents, pointing at `../explorer.html` or `../cycle-index.html`. Both pages exist at repository root, not `docs/`; review whether `../../` is appropriate for each deployment before editing.
- 1 in `docs/Novellas/BOOK_OF_THE_EVENTIDE_LEDGER.md`.
- 7 in `docs/dashboard.md`.
- 1 in `docs/library.md`. **Verified target:** `docs/Library/BOOK_SUMMARY_INDEX.md`; this PR corrects the case-sensitive relative path.
- 4 in `docs/sidebar.md` (2 target strings), including an ellipsis placeholder and a nonexistent Genesis book path.

The summary is grouped by source; preserve exact machine JSON artifact for the full 78 occurrence-level records. Historical missing references may be meaningful archival evidence. Don't create dummy targets or change source testimony to force the count to zero.

## Scope of this patch

Only the verified Library link is changed. The ten checksum mismatches, other missing links, unknown canon classifications, external Keeper signature, and posthumous custody remain unresolved. Follow-up batches require evidence and CI review.
