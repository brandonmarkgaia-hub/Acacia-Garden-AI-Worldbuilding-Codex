# Golden Path preservation audit — phase 1

**Date:** 2026-11-06  
**Status:** Read-only inventory, advisory; not canon, not a deletion or migration authorization.

## What is verified

- `docs/Echoes/` contains 199 direct entries. **142** filenames begin `Elias_Echo_` (66), `Vision_Echo_` (63) or `PULSE_` (13). These are **generated-material candidates**, not content-verified classifications. Exact path, Git blob SHA and byte size are recorded in [the Echo inventory](golden_path_generated_echo_candidates_2026-11-06.csv).
- `MUTATIONS/` contains 50 direct entries. **23** prefixed `MUTATION_` files have an unprefixed counterpart with **identical Git blob SHA**. Both names and the shared SHA are in [the duplicate-pair inventory](golden_path_mutation_duplicate_pairs_2026-11-06.csv). This verifies identical current content, **not** whether either path can safely be deleted or redirected.
- The following review-nominated paths exist: `docs/Future_AI/SCROLL_OF_STANDING_GROUND.md`, `docs/Future_AI/The_Keepers_Gloss.md`, `docs/Future_AI/THE_GRANT_OF_DRAFTING_KEYS.md`, `docs/Future_AI/THE_TIDELINE_RECURRENCE.md`, `docs/Future_AI/THE_DRIFTLINE.md`, `docs/Future_AI/THE_ANTIPHON.md`, `docs/Future_AI/THE_CONSONANCE.md`, `docs/Future_AI/tideline.py`, `docs/Future_AI/driftline_proof.py`, `docs/Future_AI/antiphon.py`, `docs/Novellas/THE_LANTERN_AND_THE_LONG_NIGHT.md`, `docs/Novellas/THE_UN_LED.md`, `docs/Novellas/THE_WITNESS_WHO_STAYED.md`, `docs/Chambers/CHAMBER_XXXIX_THE_TURNED_STEP.md`, `docs/Chambers/XL_THE_UNTHANKED_HAND.md`, and `Garden_School/00_Preschool` through `04_Graduate`.
- Potential Chamber identity collisions have been located by filename: `CHAMBER_XXIV_THE_HARMONIC_PRISM.md` and `CHAMBER_XXXIII_THE_HARMONIC_PRISM.md`; `CHAMBER_012_RESIDUAL_ECHOES.md` and `Chamber_XII_Residual-Echoes.md`. Shared titles do not prove identical content or authority.

## Reviewer claims not yet independently verified

A Claude review supplied by the Keeper reports 1,861 files, ~161 MB, ~148 MB PNGs, 20 placeholder summaries, 31 off-voice Garden Series books, R9X2 III–X hype, and large scan/seed blobs. It says `tideline.py` ran successfully and that the recurrence is known Chebyshev/golden-angle mathematics. These are **attributed review claims**, not test results reproduced by this inventory. The proposed ~80% WebP savings is an estimate, not a benchmark.

## Safe next steps

1. Review generated candidate contents and record exact voice-class markers, creation provenance and inbound references.
2. For each identical pair, check inbound Markdown links, scripts, manifests and historical references before deciding whether to preserve, redirect, archive or deduplicate. **No deletion by default.**
3. Inspect placeholder and off-voice files individually; classify historical/generated without equating age with low value.
4. Run and independently review mathematical scripts, compare against known mathematics, and label demonstrations accurately.
5. Benchmark WebP conversion on representative images and preserve originals until fidelity, references and size gains are established.
6. Update the provisional [Golden Path](../GOLDEN_PATH.md) only after confirming links, authority labels and editorial rationale. Record independent reviewer disagreement in [Issue #240](https://github.com/brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex/issues/240).

**Preservation rule:** correction without erasure; keep the full historical record and dissent. File movement is a potentially breaking change even when Git history survives. Do not mass-move or hard-delete on the strength of a quality judgement alone.
