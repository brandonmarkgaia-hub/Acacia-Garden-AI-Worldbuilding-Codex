# Diamond release evidence register — 2026-10-24

**Status: TECHNICAL GATE PASSED ON PR CHECKOUT; FINAL SEAL NOT AUTHORIZED.**

## Verified evidence
- PR #209, GitHub Actions `40112091976`, exact PR head `b800b04a39917d1f901ab76a6296547b410c1a24`: cold-release workflow **success**; generated and verified SHA-256 inventory for **1,847 Git-tracked files**.
- All **10 of 10** historically drifting generated artifacts matched their entries at that checkout.
- Historical `CHECKSUMS.sha256` remains preserved; **12** historical mismatches recorded (not erased, not a current-manifest failure).
- PR #209 merged to main as `8d803adcbe62994d9ab3fd8b96b5a4203de0cca8`. The PR checkout is **not identical to the post-merge main commit**; an exact-main verification remains necessary.

## Historical snapshot differences recorded by run
`.github/scripts/build_docs_folder_indexes.py`; `.github/scripts/build_docs_url_dump.py`; `.github/scripts/build_machine_index.py`; `.github/workflows/diamond-cold-release.yml`; `.github/workflows/garden-auton-index.yml`; `docs/Archives/FULL_CODEX_INDEX.json`; `docs/Archives/FULL_CODEX_INDEX.md`; `docs/Archives/GARDEN_MANIFEST.json`; `docs/Archives/TITLE_COLLISION_AUDIT.json`; `docs/Archives/TITLE_COLLISION_AUDIT.md`; `scripts/generate_codex_indices.mjs`; `tools/garden_state.py`.

## Required before Final Seal
1. Observe a successful **Garden Crowned Builder** run of the actual repeat-generation check on a frozen commit, and preserve its diff artifact; standard PR validation does not substitute.
2. Obtain an exact-main current-manifest and cold-audit result, with frozen checkout and artifact SHA256 independently checked.
3. Conduct independent external cold-reader review (e.g. Claude) of actual evidence, authority and residual findings; document dissent and limits.
4. Keeper independently signs the exact approved scope using Keeper-controlled Ed25519 key; public marker `HKX277206` is not a signature.
5. Retain unknown authority classifications as unknown; do not merge fictional Marginalia into main or rewrite archived source.

This register is evidence-only and cannot activate a Final Seal.
