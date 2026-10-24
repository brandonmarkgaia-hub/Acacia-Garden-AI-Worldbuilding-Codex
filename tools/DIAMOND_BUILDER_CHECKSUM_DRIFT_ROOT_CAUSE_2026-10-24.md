# Generated artifact checksum drift — source-grounded cause and policy

## Observed

The `Garden Crowned Builder (Deterministic)` workflow at `.github/workflows/garden-auton-index.yml` runs on `main` pushes touching tools, docs, scripts, and workflows. It rebuilds the ten audited files using `build_docs_folder_indexes.py`, `build_docs_url_dump.py`, `generate_codex_indices.mjs`, `build_machine_index.py`, and `garden_state.py`, and commits owned artifacts directly to `main`.

The generator sources embed current-time fields, including `datetime.now(timezone.utc)`, `new Date().toISOString()`, and `now_utc()`. Thus **the workflow title's “Deterministic” claim is not true at the byte level for time-bearing outputs**. This is a verified reproducibility defect, not evidence of malicious changes.

The builder's published `ARTIFACTS` list contains all ten paths, but **does not include `CHECKSUMS.sha256`**. Therefore a successful builder run can change the ten files while leaving the checksum manifest stale. The read-only diamond cold audit in run [40109871717](https://github.com/brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex/actions/runs/40109871717) demonstrated this state: 1,839 entries checked, 10 mismatches, 0 missing paths, and a failed technical-integrity verdict. Earlier run [40109546891](https://github.com/brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex/actions/runs/40109546891) measured 10/10 matches at a different checkout. Both results are valid **for their own commits**.

## Safe remediation policy (not yet implemented)

1. Freeze the source checkout for release; do not accept `main` as stable while the automatic builder continues to rewrite timestamp-bearing files.
2. Separate reproducible source inventories from volatile build metadata. Either derive a stable `SOURCE_DATE_EPOCH` from a pinned commit or move the generated-at clock to an untracked runtime display; verify that two builds from identical inputs produce byte-identical artifacts.
3. Decide and document a checksum ownership policy for the generated ten. If checksums attest the *current* generated artifacts, update the manifest **in the same atomic commit** as their regeneration and preserve previous manifests in Git history. If checksums attest an immutable release snapshot, do not mutate its manifest on each push; publish a separately versioned release checksum manifest instead.
4. Never silently change historical `CHECKSUMS.sha256` lines or auto-label checksum mismatches benign. Require explicit provenance, recorded before/after hashes, and reviewed policy changes.
5. Add a failing post-build checksum verification gate and re-run the full frozen-checkout cold audit after remediation.

This document diagnoses the workflow and specifies a guarded repair. It does **not** perform a checksum rewrite or claim release integrity is already fixed.

## Other cold audit residuals

Run 40109871717 also reported 48 simple relative Markdown link findings, 153 short Markdown files, and 1,391 unknown authority classifications. These are review queues, not automatically invalid content or Keeper-approved Law. Independent contradiction/threat-model/cold-reader reviews and cryptographic Keeper attestation remain open.
