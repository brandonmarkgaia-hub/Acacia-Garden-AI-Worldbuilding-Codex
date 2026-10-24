# Diamond cold release: provenance and residual-risk register

**Advisory only; no Canon, Law, Final Seal or Keeper authentication.**

## Historical mismatch attribution

The earlier ten SHA-256 mismatches were observed at GitHub Actions run 39846567770. A later independent exact-checkout run 40109546891 showed **10/10 current file digests matching the then-current CHECKSUMS.sha256**. All ten paths last changed at commit `f82a39b776f4353a2015570c0587934a0b7e4be2` (`chore: refresh Garden artifacts [auton]`). The [builder workflow](../.github/workflows/garden-auton-index.yml) explicitly owns all ten paths and rebuilds them on `main`; its generators include time-derived fields. The commit diff visibly changes generated timestamps.

**Evidence-supported conclusion:** automated rebuilds and refreshed checksum baselines explain *a plausible mechanism* for checksum drift, not a proven byte-for-byte attribution for every mismatch in the older checkout. That last attribution requires comparing historical checkout bytes, the historical checksum manifest, and the intervening commits. Do not rewrite or erase either record.

## Final cold audit

The [diamond cold release workflow](../.github/workflows/diamond-cold-release.yml) collects the full read-only corpus audit, exhaustive advisory classification inventory, ten-path exact hashes and git history, and a machine-readable release verdict on **one checkout**. It intentionally does not turn unknown documents into Law, hide broken links, mark historical drift benign, or imply a Keeper signature.

## Open gates

- Historical ten-file causality: exact historical snapshot comparison not completed.
- Generator reproducibility: volatile timestamps remain; repeat builds are not proven byte-identical.
- Remaining simple-link findings: classify genuine navigation defects versus examples/placeholders/archive evidence before repairing.
- 1,384 unknown classifications were reported in an earlier audit, not necessarily the current count; none may be automatically promoted.
- Contradiction register, adversarial threat-model expansion and independent cross-model cold-reader survey from [platinum evidence review](PLATINUM_EVIDENCE_REVIEW_REGISTER.md) remain separate unfinished governance/release tasks.
- Keeper-controlled cryptographic signature and independent public-key binding remain outstanding.

**Release discipline:** freeze a specific main SHA after any further automated builder commit, run this workflow at that SHA, review every residual item, and then arrange independent cold-reader evaluation. No Final Seal activation on a passing CI badge alone.
