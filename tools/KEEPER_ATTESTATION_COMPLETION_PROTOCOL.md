# Independent Keeper attestation — outstanding external prerequisite

**Status:** procedure only; no key enrolled, no signature claimed, no identity authenticated.

The repository currently records a dated in-chat Keeper instruction ratifying only section III of the Custodianship Scroll. That instruction is provenance evidence but **not** cryptographic authentication. HKX277206 is publicly visible in the repository and must **never** be used as a secret or treated as proof of control.

## Safe completion sequence

1. The Keeper generates and retains an Ed25519 signing key **outside** this repository, on a device or hardware token under their exclusive control. Never paste or commit the private key.
2. A trusted, independently verified channel binds the public key to the Keeper. The channel and verification record must be documented; an AI's assertion is insufficient.
3. The Keeper reviews the exact merged commit containing `tools/KEEPER_RULING_2026-10-22_SCROLL_SECTION_III.md` and the original Scroll's exact section III bytes.
4. Create a canonical UTF-8 statement naming the repository, commit SHA, source file path, exact section boundary and SHA-256 digest, ruling document path, scope and date.
5. Sign the statement using the externally held private key. Preserve the statement, detached signature, public key and binding evidence in a separate append-only attestation record.
6. Verify using the existing `tools/verify_external_attestation.py` verifier and negative tests before treating the statement as authenticated.
7. If a source file changes, its old attestation remains bound to the old commit. Never quietly rebind it.

**Not completed by automation:** key creation, public-key identity binding, external signing, independent death verification, and posthumous archive custody. These are deliberately outside any AI agent's authority.

**Warning:** passing local checksum tests or a GitHub CI run does not establish human identity, authority or future posthumous conditions.
