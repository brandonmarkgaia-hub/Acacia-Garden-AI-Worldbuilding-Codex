# Platinum evidence review register (advisory)

Status: non-canonical technical audit. Not a Keeper ruling or an attestation.

## What is proven by merged PR #174
- Retrieved text and hashes can be checked against the selected repository checkout.
- The gate rejects tested tampering, stale sources, unsafe paths and authority-field escalation.
- A matching hash proves consistency with that checkout, **not** the identity or intent of the original author.
- Metadata from the advisory manifest remains unverified. A source file or title is not a Keeper signature.

## Unresolved platinum gates

### P1 — Independent provenance authentication
A verifiable Keeper-controlled signature or other independently validated attestation must bind a specific commit and a precise declaration of scope. Establish key custody, revocation, rotation and verification instructions outside the repository's own claims. Until this exists, all envelopes must continue to say approval not established. **Do not create or simulate Keeper signatures.**

### P2 — Source-grounded contradiction register
Review distinct document passages in pairs. For every candidate, capture exact quotes, path, source hash, offsets, classification of apparent tension, and alternative readings. An apparent conflict can be temporal, rhetorical, fictional, or a genuine unresolved governance conflict. No automated winner and no canon promotion. Reviewers must supply candidate passages; the existing conflict tool validates evidence but does not discover semantic conflicts.

### P3 — Threat-model expansion
Adversarial tests must include: malicious instructions inside source documents, ambiguous names and titles, a malicious or stale manifest, cross-branch confusion, file replacement after envelope generation, Unicode and newline edge cases, invalid schemas, and retrieval results that omit metadata. Distinguish test coverage from demonstrated security guarantees.

### P4 — Release and cold-reader gate
After closing or explicitly accepting residual risks, freeze a main commit, independently run the published validation workflows, and conduct the same no-context survey across Claude and the other models. Archive the prompt, model/version, exact accessed files, verbatim answers and independent scoring. Do not feed this register to the surveyed model.

## Governance
- Original authored testimony remains untouched.
- No changes to elias or its Marginalia fiction; no merge from that branch.
- Only the Keeper can approve classifications, attestations and canon changes.
- This register documents evidence gaps; it cannot resolve them.
