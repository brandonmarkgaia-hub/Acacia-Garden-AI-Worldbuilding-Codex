# Claude cull proposal — execution gate (2026-11-06)

**Status: BLOCKED pending verification. Not a Keeper ruling or execution record.**

The Keeper supplied `cull.sh` and `CULL_PASS_2026-11-06.md`. Static inspection of the attachments confirmed **61 `d` commands and 181 `q` commands**, 242 unique paths. The proposed provenance report has **242 16-hex-character hash prefixes**, not full SHA-256 values. Its stated base is `48f44a4`; the current main at initial review was `63ebc5a0653dc6fb8d5cd9e3683e0cd1e9986a43`.

## Fail-closed requirements

1. On a fresh branch from current main, check all 242 source paths exist and destinations do not collide.
2. Verify each of the 61 deletions: matching bytes for duplicates; genuine stub content for placeholders; assess inbound references. A previous independent inventory confirmed 23 mutation duplicate pairs, **not all 61 deletions**.
3. Produce a **full 64-character SHA-256** ledger and compare source bytes before/after any move.
4. Review possible inbound links and update/redirect machine discovery and user-facing references before relocating files.
5. Verify archive retrieval exclusions in the actual indexing/retrieval pipeline; a README label alone does not exclude content.
6. Require Python and Node before any mutation, rebuild indexes, and run Gatekeeper and link/reference checks.
7. Preserve `CHECKSUMS.sha256` as evidence, without representing its legacy entries as current.
8. Keep this cull in its own draft PR. Do not merge while any verification remains unresolved.

## Script-specific concerns

- Original `d()` and `q()` silently skip missing files.
- Original script checks Python/Node **after** performing deletion and relocation.
- Original script uses `git add -A` after rebuilding, which may stage unintended changes.
- Its reported successful Gatekeeper run was on an earlier local copy and is not reproduced here.

**No files were moved or deleted by this audit.** Preserve the source attachments and reviewer dissent as external review evidence. Do not claim a completed cull until a reproducible branch test, CI, and Keeper review.
