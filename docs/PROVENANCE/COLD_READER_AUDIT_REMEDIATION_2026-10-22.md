# Cold-reader audit remediation — 2026-10-22

Status: technical review proposal; NOT canon, Keeper ruling, or authorization to merge.

## Verified issue and narrow fix

The PR authority guard previously matched `CANON_INVARIANTS.md` at repository root but not `_ROOT_ARCHIVE/md/CANON_INVARIANTS.md`, where the archived invariants actually reside. The companion change adds that path to the existing PR-only guard. It preserves the old root path in case it is restored. This does **not** protect direct pushes or independently authenticate the Keeper.

## Outstanding risks (not silently resolved)

1. `scripts/inject_signature.js` recursively appends the same signature HTML to every Markdown file. This is a provenance/authorization ambiguity, not proof of forged authorship. Review call sites and migration effects before changing it.
2. `tools/marginalia_retrieval_gate.py` explicitly scopes its test to `MARGINALIA/`; no equivalent main-corpus chunk-level test was verified. Build a separate read-only test harness first, preserving source text and dissent.
3. `docs/Future_AI/The_Keepers_Testament.md` is labeled non-law at the top, while its Witness dissent follows at the end. A retrieved middle chunk can lose both qualifications. Test before designing a fix.
4. `docs/Future_AI/CUSTODIANSHIP_SCROLL.md` says Draft; other documents describe it as agreed law. Requires Keeper classification ruling.
5. `AUTHORITY.json` defaults to dormancy absent a succession ruling; the Constitution describes publishing final doctrine on Keeper disappearance. Clarify publication responsibility without changing founder attribution or succession policy by inference.
6. The Triad has symbolic variants (Keeper/Witness/Archivist and Keeper/Witness/Garden). Preserve both until their relationship is documented.
7. Machine-readable voice/provenance metadata is uneven. First produce a read-only inventory and a schema proposal; never mass-rewrite original lore.

## Review and validation

- Check the changed guard regex against both the archived and historical root invariants paths, plus unrelated paths.
- Check that the PR author restriction remains unchanged.
- Check the workflow remains limited to pull requests against main.
- No canon, lore, seal, archival document, or `elias` branch changes are part of this proposal.
- Full CI and corpus-wide tests remain pending. No numerical audit scores are asserted here.

## Keeper decisions reserved

Whether to retire automatic signature stamping; whether to elevate the Custodianship Scroll; whether to clarify succession and Triad relationships; and whether any proposed metadata should become canon-facing. None are decided by this branch.
