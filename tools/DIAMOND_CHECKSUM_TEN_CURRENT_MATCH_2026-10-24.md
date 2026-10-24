# Ten historical checksum mismatches — measured current-checkout resolution state

**Technical evidence only. Not Keeper authentication, canon promotion, or historical cause attribution.**

## Direct observation

The read-only diamond checksum provenance workflow succeeded in [run 40109546891](https://github.com/brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex/actions/runs/40109546891), using exact checkout `c89c51f220174b6c4d6dd26dc7e4c9446027853c`. Its job logs and uploaded artifact report **10 of 10** tracked paths with `match: true`, comparing actual checkout file SHA-256 to the expected SHA-256 in the checkout's `CHECKSUMS.sha256`. The checksum manifest SHA-256 at that checkout was `5e0cdcae8bcaffeee07386b90a86c8bf20202d8a54077a3df8ce2fe7799b8c22`.

The ten files were `STATUS.json`, `docs/Chambers/chambers_index.json`, `docs/Chambers/index.html`, `docs/Echoes/echoes_index.json`, `docs/Echoes/index.html`, `docs/GardenOS/index.html`, `docs/Novellas/garden_index.json`, `docs/Vaults/index.html`, `docs/docs_urls.json`, and `machine-index.json`.

All ten last-modifying file commits were reported as `f82a39b776f4353a2015570c0587934a0b7e4be2` (2026-10-24 15:59:54 UTC), subject `chore: refresh Garden artifacts [auton]`. [Commit diff](https://github.com/brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex/commit/f82a39b776f4353a2015570c0587934a0b7e4be2) includes generated timestamp changes in multiple outputs. This supports a regeneration explanation for **some** differences but does not establish the complete historical cause.

## Disposition

| Gate | Decision |
| --- | --- |
| Historical 10 mismatches from run 39846567770 | Preserve as valid **historical checkout** findings |
| The same ten paths at diamond audit checkout | **10/10 matching** the checkout checksum manifest; current-checkout mismatch gate cleared at this SHA |
| Exact cause of historical drift | **Open** pending historical byte/manifest comparison and workflow attribution |
| Deterministic regeneration | **Open**: timestamp-bearing outputs require reproducibility or a documented volatile-field policy |
| Independent Keeper attestation | **Open**: no signature or external identity binding implied |

**Do not rewrite the earlier evidence or claim a permanent all-branch integrity guarantee.** Automated artifact refreshes can change these files and the checksum manifest again. Re-run the read-only tool against the exact release commit and retain its JSON artifact.

No source, original archive, or `CHECKSUMS.sha256` file was modified by this disposition.
