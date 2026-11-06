# Diamond release — verified current findings (2026-10-24)

**Status: HOLD — not a final seal.** This report records GitHub Actions evidence without changing any source, checksum, archive, or authority classification.

## Confirmed control changes

- PR #198: read-only builder containment and fail-closed cold-audit gate merged.
- PR #199: five timestamp-generating programs changed to derive stable Git commit timestamps.
- PR #202: ten generated outputs rebuilt twice with SHA-256 equality required in builder.
- PR #204: builder checkout pinned to triggering commit rather than moving main.
- PR #205: repaired the cold-audit diagnostic YAML indentation and merged.

## Frozen checkout audit evidence

At PR #205 head `8e1602c67d8bc7f47c4c86027eb86a1f1049886f`, GitHub Actions run [40111636507](https://github.com/brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex/actions/runs/40111636507) reported **8 checksum mismatches**, and `technical_integrity_gate_passed=False`. Its exact mismatch paths were:

1. `.github/scripts/build_docs_folder_indexes.py`
2. `.github/scripts/build_docs_url_dump.py`
3. `.github/scripts/build_machine_index.py`
4. `.github/workflows/diamond-cold-release.yml`
5. `.github/workflows/garden-auton-index.yml`
6. `docs/Archives/GARDEN_MANIFEST.json`
7. `scripts/generate_codex_indices.mjs`
8. `tools/garden_state.py`

All ten formerly drifting generated outputs matched in that particular audit. **This is not proof of a clean release.** Seven mismatch paths are recently edited implementation/workflow files, and the remaining archival manifest needs independent source and checksum provenance review. A mismatch is not waived merely because its source was intentionally edited.

## Required release decisions

1. Preserve the existing `CHECKSUMS.sha256` as historical evidence until the Keeper approves a documented release-manifest scope and versioning policy. Do not quietly rewrite old hashes.
2. Verify repeat-generation equality on an actual completed pinned builder workflow run; code presence and ordinary CI green checks are insufficient.
3. Produce a separate, reviewed release checksum manifest for a fixed checkout (if approved) and attest its exact scope without replacing archival evidence.
4. Independently inspect `docs/Archives/GARDEN_MANIFEST.json` for whether it is immutable evidence or a generated file, and document its history before deciding treatment.
5. Re-run the full cold audit at a frozen release commit; classify remaining link findings and unknown authority documents without automatic promotion.
6. Independently bind the Keeper's public key and obtain a Keeper-controlled Ed25519 signature. HKX277206 is a public marker, **not** a cryptographic key.
7. Obtain an external cold-reader review and record dissent/residuals before any final seal.

This report is evidence-only, not authorization to change archival sources, reclassify canon, or activate a Final Seal.
