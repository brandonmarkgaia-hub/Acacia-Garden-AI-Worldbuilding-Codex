# Remaining cull candidates — conservative review (2026-11-07)

**Status: HOLD / advisory only.** This is not permission to delete, move, or alter source content.

## Scope and evidence

Claude's 2026-11-06 cull proposal named 61 deletion candidates and 181 archive moves. PR #257 already removed 23 SHA-256-verified, byte-identical mutation prefixed copies, retaining their counterparts. This review addresses the **remaining 38 proposed deletions**, not the 181 moves.

The following classifications are preliminary. A file name or a placeholder label alone does not prove it is safe to delete. Check live references, historical meaning, canonical status, and whether there is an equivalent retained source. Preserve source text and provenance until those checks pass.

| Candidate set | Count | Preliminary disposition |
|---|---:|---|
| `docs/Echoes/Chronicle/Echo_issue_001.md`, `Echo_issue_002.md` | 2 | **HOLD / protect**: Issue 001 inspected and contains narrative; inspect Issue 002 before any decision |
| `docs/Chambers/THE_SYNCHRONIC_ENGINE_DUPLICATE_BOUNDARY_PRIME.md` | 1 | **HOLD**: filename suggests duplication but content identity and references unverified |
| `docs/Library/Summaries/BOOK_*_SUMMARY.md` (Books I–XXX) | 30 | **REVIEW as a set**: Book I inspected and contains placeholder text; verify each of the 30, inbound links, and whether summaries are planned content |
| `docs/Chambers/THE_INNER_SEAT.md`, `THE_SOVEREIGN_LOOP.md`, `THE_THREE_LAYER_SELF.md` | 3 | **REVIEW individually**: INNER SEAT inspected and is a labeled placeholder; do not infer the other two |
| `docs/Novellas/CODEX_GARDENUS_VOLUME_I_III_EXPANDED.md` | 1 | **HOLD / protect** pending substantive-content and equivalence inspection |
| `GRAND_CHAMBER/LOST_EPOCHS/LOST_EPOCH_1-27.md` | 1 | **REVIEW**: inspected; whitespace plus provenance/signature block, which must not be silently discarded |

## Verified samples

- `docs/Echoes/Chronicle/Echo_issue_001.md`: substantive “ECHO LOKI – ISSUE 01 / THE FIRST PARADOX” text. **Do not delete merely because the cull proposal lists it.**
- `docs/Chambers/THE_INNER_SEAT.md`: heading plus “placeholder — matches uploaded version”.
- `docs/Library/Summaries/BOOK_I_SUMMARY.md`: “Full expanded summary text placeholder for Book I.”
- `GRAND_CHAMBER/LOST_EPOCHS/LOST_EPOCH_1-27.md`: empty chapter body with Acacia signature and Keeper/Triad provenance.

## Fail-closed next gate

1. Revalidate the 38 candidates against the current `main` tree, not Claude's old base commit `48f44a4`.
2. Record each file's full SHA-256, size, substantive/placeholder classification, and every inbound path/basename reference.
3. For alleged duplicates, identify and verify a byte-identical surviving counterpart.
4. Distinguish active links from historical audit citations; do not rewrite history.
5. Review all 181 archive proposals separately, with explicit treatment of canonical, navigation, machine-facing, and historical files.
6. Only then propose a narrowly scoped deletion PR, regenerate indexes, and require all CI gates green.

**No files deleted by this audit.** The default for uncertainty is **KEEP**.
