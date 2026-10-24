# Legacy findings — evidence triage (2026-10-24)

**Status:** Technical audit note, not Canon or an attestation. Do not rewrite original archive content or historical checksums on this evidence alone.

The CI artifact for [run 39846567770](https://github.com/brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex/actions/runs/39846567770) includes 10 checksum mismatches and 78 simple relative-link findings **at that historical checkout**. A passing audit means the report was generated, not that the findings were resolved.

## Ten checksum mismatches (as recorded in the artifact)

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

These are predominantly machine-readable indices or rendered HTML. **That pattern suggests** regeneration may explain some mismatches, but is not proof. Verify each expected hash, current bytes, generating workflow and last modifying commit before deciding whether to regenerate the checksum index. Preserve historical checksum values as evidence.

## Link findings: where they concentrate

- `_ROOT_ARCHIVE/md/garden_scan_report.md`: 37 findings, many pointing to paths under `../Echoes/Issues/` from an archived report. Treat this as historical output; do not silently edit.
- `docs/Cycles/` eight documents: 22 findings to `../explorer.html` or `../cycle-index.html` in the artifact. **Current main versions inspected already use `../../explorer.html` and `../../cycle-index.html`.** These findings may be obsolete on the current branch; compare checkout SHAs before proposing further edits.
- `docs/dashboard.md`: seven uppercase root paths; check whether those are historical aliases or should resolve to modern `docs/` directories.
- `docs/ACACIA_SPECS/ARCHETYPE_PROMPT_SCHEMA.md`: three paths occur in explanatory examples or legacy embedded material. Do not automatically rewrite example text.
- `docs/sidebar.md`: links to literal `...` are placeholders, not real navigable destinations. Review sidebar design rather than inventing book files.
- `docs/library.md`: one incorrect `../LIBRARY/BOOK_SUMMARY_INDEX.md` path. Current verified target is `docs/Library/BOOK_SUMMARY_INDEX.md`; this PR fixes that reference only.
- `docs/Novellas/BOOK_OF_THE_EVENTIDE_LEDGER.md`: one missing Echo issue path; inspect intended historical referent before repair.

**Counts are not a current-main claim.** Rerun the read-only audit on the exact current checkout and compare individual findings; do not assume all 78 remain broken.

## Classification and attestation

The 1,384 unreviewed documents remain unknown by default. An inventory is not a complete list of Law. A real Keeper-controlled Ed25519 signature, independently bound public key and signed exact scope remain prerequisites; neither an AI-written document nor the public HKX277206 marker substitutes for them.

## Safe follow-up

Review each current-checkout mismatch and broken link; distinguish generator drift, legacy archival references, placeholders and real broken navigation. Make small, testable PRs with source-path evidence. No automatic canon promotion, `elias` merge, Final Seal activation or checksum mass refresh.
