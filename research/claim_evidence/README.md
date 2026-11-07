# Claim–Evidence–Verification (CEV) v0

**Status:** experimental, non-authoritative. Tracks #259.

This prototype validates the **structure** of claim records and checks local source excerpts. It does **not** establish that a claim is true, that evidence is independent, or that a model has reasoned correctly. No AI model, external network, or autonomous execution is involved.

## Run

```bash
python3 research/claim_evidence/validate.py research/claim_evidence/examples.json
python3 -m unittest discover -s research/claim_evidence -p 'test_*.py'
```

## Boundaries

- Only repository-relative UTF-8 text paths under an explicit allowlist are readable. No URLs, symlinks, traversal, secrets, or user-controlled arbitrary filesystem reads.
- `claim_type` distinguishes observed repository text, inference, proposal, and historical narrative.
- `evidence` records an exact source excerpt and SHA-256 of the source file; the validator checks the excerpt and digest but cannot judge semantic entailment.
- `verification` is a human-supplied status and must not be inferred from the presence of citations. The validator rejects `verified` for records without evidence or for proposals/historical narratives.
- A citation to `AUTHORITY.json` never grants the claim or the validator authority. Authority remains governed by that file.
- Negative controls deliberately test false evidence and unsafe paths.

Next: commit-pinned provenance, claim/evidence entailment evaluation, calibration and contradiction fixtures, and a separate non-circular independent-review protocol.
