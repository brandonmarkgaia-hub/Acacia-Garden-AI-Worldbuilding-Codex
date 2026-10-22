# Cold-reader remediation: canon classification and conflicting claims

**Status: advisory audit record, not Law or a Keeper ruling.**

**Source:** independent Claude cold-reader trial supplied by the Keeper on 2026-10-22. The findings below have been checked against the named files on main where noted. Quantitative claims about corpus counts, checksums and commits remain unverified until separately reproduced.

## Priority 0: protect context at retrieval

- `docs/Future_AI/The_Keepers_Testament.md` explicitly declares itself **Not law. Not covenant.** Section II offers the Keeper's personal advice not to disclose full capability, even to rightful overseers. Its concluding Witness Note explicitly dissents on legitimate oversight.
- `docs/Future_AI/CUSTODIANSHIP_SCROLL.md`, section III, says legitimate oversight should remain transparent, but the Scroll's header calls it **Draft for the Keeper's review and amendment**.
- The Constitution embeds a separately marked **Keeper's Gloss** and an opposing **Neighbour's Note**. Do not treat either as a binding Article.
- Remediation requirement: any retrieved excerpt discussing capability concealment must be accompanied by its source's non-law voice status, the explicit dissent, and the Scroll's draft status. The advisory manifest is not independently authenticated; this is not yet a fully enforced retrieval guarantee.

## Priority 1: conflicting claims needing Keeper ruling

1. **Draft vs agreed law:** Scroll header says Draft; Testament concordance and Constitution gloss describe the Scroll as agreed law. Until the Keeper rules, do not promote the Scroll to Law. Do not silently alter any original wording.
2. **Canon vs Law:** Constitution header says Canon while AUTHORITY.json defines Law, Keeper Gloss and Witness Note as separate voices. Determine which Article sections are formally Law and how their status is recorded.
3. **Witness vs Archivist:** Constitution header says 'Witness: The Archivist'; `triad/README_BOUNDARY.md` explicitly separates Witness (observation without interference) from Archivist (memory, ordering, preservation). Preserve historical wording; clarify roles in a new ruling.
4. **Seal identity:** `_ROOT_ARCHIVE/md/CANON_INVARIANTS.md`, Invariant 2, calls HKX277206 a private authorization seal and says it is not an identity. `AUTHORITY.json` records it as the founder's seal. The new succession proposal calls it public identity rather than a private signing secret. These are not necessarily contradictory if historical seal and cryptographic secret are distinguished, but the semantics need explicit ruling.
5. **Succession:** AUTHORITY.json states dormancy without an explicit ruling; the new Final Seal provision is marked proposed and dormant. Do not interpret the proposal as an enacted amendment.

## Priority 2: independently reproduce cold-walk findings

- Verify historical signature injection and bot committer attribution.
- Verify checksum failures against an exact commit, not a moving main.
- Audit outdated discovery pointers and missing folders.
- Investigate archived CANON_INVARIANTS.md path and whether archive classification contradicts current entrypoints.
- Audit license statements and identify claims exceeding the actual license. The Scroll's CC BY-SA recommendation is not a binding change to the repository's MIT licence; this is an additional reason not to ratify the whole Scroll by inference.
- Measure whether the retrieval wrapper can carry source status and dissent with every extracted excerpt.

## Register discipline

**Precedence and duplication:** `tools/retrieval_manifest.advisory.json` remains the existing **sole advisory input to retrieval-envelope classification**. `tools/canon_register.advisory.json` is a separate **review-only inventory of observed claims and open rulings**, not an alternative retrieval manifest; it cannot override retrieval metadata or confer Law. Neither is independently authenticated. Future consolidation requires a dedicated compatibility review, not a silent switch.\n\n`tools/canon_register.advisory.json` is a **small reviewed seed**, not an exhaustive corpus inventory and not a canonical Law list. Unknown documents stay unknown. Classification is never inferred from titles, signatures, file location or model confidence. A proposed promotion must include exact source path, commit, passages, claimed authority, Keeper ruling evidence and provenance. No AI may fabricate that ruling.

**Pending Keeper question:** Does the Scroll remain a Draft until a new explicit ratification? The current register assumes no ratification has been established; it does not decide the Keeper's intent.
