# Legacy audit findings and controlled remediation — 2026-10-24

**Status:** Technical triage, not Canon or Keeper attestation. No historical documents or CHECKSUMS.sha256 are rewritten by this report.

## Reproducible measured baseline

GitHub Actions run [39846567770](https://github.com/brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex/actions/runs/39846567770) completed successfully on the PR #183 audit implementation and uploaded artifact [12455228351](https://github.com/brandonmarkgaia-hub/Acacia-Garden-AI-Worldbuilding-Codex/actions/runs/39846567770/artifacts/12455228351).

Measured summary from job logs:

| Metric | Count | Interpretation |
| --- | ---: | --- |
| Markdown files | 1,387 | Files discovered by read-only audit |
| Unknown classification | 1,384 | **Not** a claim that only 3 files have meaningful authority; only 3 are reviewed in the advisory retrieval manifest |
| Markdown files shorter than 300 characters after signature removal | 155 | Triage candidates; not automatically empty or invalid |
| Signature footers | 350 | Attribution ambiguity; not proof of authorization or forgery |
| SHA-256 entries checked | 1,826 | Entries in legacy CHECKSUMS.sha256 |
| SHA-256 mismatches | 10 | Needs individual review of changed source versus stale checksum; do not silently rewrite |
| Missing checksum paths | 0 | No missing file among parsed entries |
| Missing simple relative Markdown links | 78 | Potential broken links; parser has known limitations |

These counts are scoped to the run's checkout, not a guarantee that they remain unchanged on future main commits.

## Safe closure criteria

1. **Checksum mismatches:** inspect each exact path and Git history; classify stale index, intentional post-index edit, format issue, or actual integrity concern. Record original expected digest, current digest, historical commit and review decision before proposing any checksum refresh. Never use a blanket `sha256sum` rewrite to erase evidence.
2. **Links:** inspect all 78 findings; check percent-encoding, relative path base, case, anchors, Jekyll URL conventions and intended target. Repair only verified broken references in new commits, not historic content where preservation has precedence. Update audit logic for known false positives and add tests.
3. **Short files:** distinguish intentional stubs, archived artifacts and empty placeholders. Do not auto-fill or delete.
4. **Footers:** audit `scripts/inject_signature.js` call sites and provenance before changing stamping; a repeated public seal is not cryptographic proof.
5. **Classification:** every one of 1,384 unknown entries remains unknown until evidence-based review. Do not bulk-promote to Law or infer from headings, filenames, git personas, signature footer or AI confidence.
6. **Keeper authentication:** `tools/KEEPER_ATTESTATION_COMPLETION_PROTOCOL.md` remains a prerequisite, not a completed signature. Independent key binding, Keeper-controlled signing and verification require the human Keeper's participation.

## Guardrails

- The original Scroll remains historically Draft; its section III ruling is an additional, dated layer.
- Preserve Testament non-law status and Witness dissent.
- No `elias` branch merge; no Final Seal activation or succession inference.
- Run `python -m unittest -v tools/test_corpus_integrity_audit.py`, `python tools/corpus_integrity_audit.py --root .`, and `python tools/exhaustive_canon_inventory.py --root .` after each reviewed batch.
- Never call a successful audit workflow proof of clean integrity. A successful run means the tools executed and reports were produced; it does not mean the reported defects are resolved.

## Status

**Audit tooling and baseline: completed.** Individual legacy-file remediation, exhaustive human-governed classification, and external cryptographic Keeper attestation: **open**. Do not close those workstreams without corresponding reviewed evidence.
