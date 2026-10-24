# Current release manifest policy (v1)

**Decision (Keeper-approved):** Preserve `CHECKSUMS.sha256` byte-for-byte as historical evidence. Do not restamp it or interpret its stale entries as proof of corruption. Generate a **separate** current-checkout release manifest under `releases/CURRENT_RELEASE_MANIFEST.v1.json` as a CI artifact, not an automatically committed file.

Run `python tools/current_release_manifest.py --write` on a fixed checkout, then `python tools/current_release_manifest.py --verify`. The GitHub Actions workflow `Current release manifest evidence` generates, verifies, and uploads that JSON for independent review. It does not push, modify the historical checksum file, alter archives, promote canon, or sign for the Keeper.

**Scope:** All Git-tracked regular files (not ignored/untracked files), sorted by path, excluding the historical checksum file and the output manifest itself. Includes source, workflows, archival files and generated tracked indexes. Any tracked symlink or missing file fails closed. The artifact includes the exact checkout commit and SHA-256 of the historical checksum snapshot. A future manifest version must explicitly change its schema/scope.

**Limitations:** This is a checksum inventory of a checkout, not independent authenticity, an immutable timestamp, a reproducible-build proof, or Keeper cryptographic attestation. A generated artifact can accurately describe compromised input; verify source provenance separately. Existing legacy `CHECKSUMS.sha256` mismatches remain openly recorded. The separate current-release manifest is **not** a substitute for the cold audit residual register or Keeper-controlled Ed25519 signature.

**Release procedure:** freeze the exact commit, inspect cold-audit residuals and repeat-build evidence, run the current manifest workflow on that commit, preserve its artifact and independently review entries. Sign the approved manifest's exact bytes only through the Keeper's separate key and procedure. Do not claim Final Seal merely because CI is green.
