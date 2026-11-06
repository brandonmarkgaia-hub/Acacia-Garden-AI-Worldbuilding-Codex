# Independent integrity anchor: Diamond verification contract

Status: PROPOSAL ONLY. No independent anchor or Keeper attestation has been established.

## Security boundary

A checksum inventory committed beside the files it covers is not independent evidence. An attacker who can edit both can create a matching pair. A workflow that generates a manifest and then verifies its own output only proves internal consistency.

## Preserve and distinguish evidence

- Preserve the existing CHECKSUMS.sha256 as historical evidence. Do not restamp it to clear mismatches.
- Report every legacy mismatch, missing file, duplicate path, malformed line, and uncovered tracked path against the exact checkout.
- Propose a separate, versioned current inventory with complete tracked-path coverage and reviewed, explicit exclusions. Record its source commit, path normalization rules, and SHA-256 digest.
- Do not treat the new inventory as trusted merely because it was generated successfully.

## Required independent attestation

An external reviewer, using a channel outside this repository and its Actions artifacts, must authenticate a statement binding the exact repository identity, commit SHA, inventory digest, exclusion policy, review scope, unique challenge, expiration, and signer identity.

The verifier must check the signature against a fingerprint independently established before reviewing the pull request. A public key supplied solely by the same pull request is not an independent anchor. A passing technical check is not a grant of Keeper, canon, or future-AI authority.

## Required negative tests

Reject absent or empty inventories, omitted or duplicated tracked paths, malformed entries, path traversal and unsafe symlinks, altered content, co-updated content and checksum without a matching independent attestation, forged signer keys, stale commits, expired or replayed challenges, changed exclusions, and modifications to the verifier or required workflow from untrusted pull-request code.

## Evidence retention

Record exact source SHA, verifier version, inventory digest, signer fingerprint and independent provenance, challenge, signature outcome, file coverage counts, unresolved legacy findings, and SHA-256 digests of evidence artifacts. Store a durable read-only evidence copy outside short-lived CI artifacts.

## Release hold

The existing Diamond cold-release gate must remain fail-closed until implementation, adversarial testing, independent review, and an actual external attestation. Do not replace its false independent-anchor flag with a hardcoded true value.
