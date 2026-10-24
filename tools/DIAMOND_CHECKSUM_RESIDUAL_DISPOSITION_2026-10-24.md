# Diamond checksum residual disposition — 2026-10-24

Status: **OPEN / evidence only; not a release seal or Keeper attestation**.

## Verified cold audit
PR #205 checkout `8e1602c67d8bc7f47c4c86027eb86a1f1049886f`, GitHub Actions run `40111636507`, reported **8 checksum mismatches**; the ten historically drifting generated artifacts all matched their existing manifest entries. The cold audit exited nonzero, correctly.

Mismatches (verbatim from the run):
- `.github/scripts/build_docs_folder_indexes.py`
- `.github/scripts/build_docs_url_dump.py`
- `.github/scripts/build_machine_index.py`
- `.github/workflows/diamond-cold-release.yml`
- `.github/workflows/garden-auton-index.yml`
- `docs/Archives/GARDEN_MANIFEST.json`
- `scripts/generate_codex_indices.mjs`
- `tools/garden_state.py`

Seven paths are audit/builder code and workflows modified during the reproducibility/containment work; their recorded checksums no longer represent the checked-out bytes. This is **not** evidence of tampering by itself, nor permission to silently rewrite a historical manifest.

The eighth path, `docs/Archives/GARDEN_MANIFEST.json`, is an archival inventory. Its origin, intended regeneration semantics, and the commit where its bytes diverged must be independently established before any remediation. No automated archive mutation is authorized.

## Required release policy decision
Determine whether `CHECKSUMS.sha256` is an immutable historical snapshot or a living checkout-integrity manifest. If immutable, preserve it and introduce a separate, explicitly scoped, versioned current-release manifest with a clear generation and review protocol. If living, update it only in a reviewed atomic commit after verifying every changed path and retaining the prior manifest and a change log as evidence. Do not auto-promote, rewrite archived source, or equate a successful technical checksum audit with Keeper signature.

## Outstanding
- Re-run repeat-build SHA256 check on the pinned checkout and preserve run evidence.
- Independently inspect Git history and content of `docs/Archives/GARDEN_MANIFEST.json`.
- Approve a manifest scope policy and audit its implementation.
- Obtain independent Keeper-controlled cryptographic attestation, if a Final Seal is desired.

Keeper marker `HKX277206` is a label, not cryptographic proof.
