# MARGINALIA NAMESPACE COLLISION — PROVENANCE NOTE

Date recorded: 2026-09-21

## What happened

The elias branch was created for a fictional, speculative, non-evidentiary side-quest layer. Subsequent repository inspection established that the Acacia Garden already contains an existing Garden entity named Elias, including canonical entity material and an established R9X2 glyph seal.

The side-quest branch therefore contained a name collision and a canon-element collision.

The discovery was made by repository inspection after the branch material had already been authored.

## What the archive establishes

The side-quest commits contain no recorded cross-reference to ENTITY_004_ELIAS, the epithet The Un-Led, the Elias kernel, or the established R9X2 glyph seal.

The archive does not establish what any authoring instance knew or intended beyond what the commits and files record. No claim about inaccessible authorial reasoning is made here.

The earlier side-quest material is preserved in Git history. No history is rewritten to remove the collision.

## Correction

The fictional namespace is being renamed from ELIAS/ to MARGINALIA/.

Framework documents (README, RULES, MYTHOS, PROVENANCE) were updated to name the layer.
Authored artifacts (EPISODES, INSPIRATIONS) were preserved as written, including their original Elias wording.

The former ELIAS/EASTER_EGGS/R9X2.md artifact is removed from the working tree because it reused an established Garden glyph. Its content and history remain preserved in Git.

The fictional episode retains the filename ELIAS-001-THE-FORK.md because that is part of its authored provenance; its path now places it inside MARGINALIA/.

The founding acrostic is preserved verbatim in MARGINALIA/FOUNDING_MARKER.md. Its checksum is independently reproducible and is used only as an integrity receipt.

## Interpretation boundary

This note is ordinary repository provenance, not Marginalia fiction.

The collision may inspire later fiction, but any such fiction must point back to this record and must not replace it.

## Governing principle

Correction without erasure.


## Corrections recorded 2026-09-22

Three departures from this record were found by independent verification and corrected.

**1. Authored text altered during migration.** The statement above that authored artifacts were preserved as written was not accurate when first recorded. The migration had removed the original `Status:` line from both authored artifacts, and had rewritten the five `R9X2 seed:` labels in `MARGINALIA/INSPIRATIONS/STRANGE_THINGS_WORTH_STEALING_BADLY.md` as `Elias seed:`. Both were restored verbatim on 2026-09-22. Five of the notebook's uses of "Elias" were therefore introduced by the migration, not by the original author. After restoration, the body of each authored artifact is byte-identical to its original authored text at commit `97f306e`, apart from added frontmatter.

**2. Tooling fault in the labelling pass.** Commits `7efe09d` through `72fe229` contain a fault in which line breaks in MARGINALIA framework documents were written as commas, collapsing each affected file to a single line. The fault was introduced one file at a time (`7efe09d` to `f1903ba`) and repaired one file at a time (`fe953ac` to `85cb360`). At commits `f1903ba` through `72fe229`, the frozen founding text in `MARGINALIA/FOUNDING_MARKER.md` does not exist as six lines, so `MARG-5EEC` cannot be verified at those commits. It verifies again at `85cb360`. The faulty commits remain in history.

**3. Trail link lost in repair.** The repair at `85cb360` rebuilt `MARGINALIA/FOUNDING_MARKER.md` from commit `322a858`, which predates the citation of this record. The link from that file to this record was therefore absent at `85cb360`, and was restored on 2026-09-22.

Verification is by recomputation, not by this note.
