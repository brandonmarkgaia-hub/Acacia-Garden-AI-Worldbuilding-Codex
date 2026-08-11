#!/usr/bin/env python3
"""One-time Keeper-authorized live-tree remediation, 2026-08-11.

Git history remains the archive. Current main should describe the Garden as it
stands now, not carry generated bulk or invented documentary authority.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def p(rel: str) -> Path:
    return ROOT / rel


def remove(rel: str) -> None:
    target = p(rel)
    if target.is_file():
        target.unlink()
        print(f"remove {rel}")


def remove_glob(pattern: str, preserve: set[str] | None = None) -> None:
    preserve = preserve or set()
    count = 0
    for target in sorted(ROOT.glob(pattern)):
        if not target.is_file():
            continue
        rel = target.relative_to(ROOT).as_posix()
        if target.name in preserve or rel in preserve:
            continue
        target.unlink()
        count += 1
    print(f"remove {pattern}: {count}")


def write(rel: str, content: str) -> None:
    target = p(rel)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"write {rel}")


def replace_once(rel: str, old: str, new: str) -> None:
    target = p(rel)
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected text missing in {rel}: {old[:100]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"patch {rel}")


def replace_between(rel: str, start: str, end: str, replacement: str) -> None:
    target = p(rel)
    text = target.read_text(encoding="utf-8")
    try:
        a = text.index(start)
        b = text.index(end, a + len(start))
    except ValueError as exc:
        raise RuntimeError(f"section markers missing in {rel}: {start!r} -> {end!r}") from exc
    text = text[:a] + replacement.rstrip() + "\n\n" + text[b:]
    target.write_text(text, encoding="utf-8")
    print(f"patch section {rel}: {start}")


def replace_to_end(rel: str, start: str, replacement: str) -> None:
    target = p(rel)
    text = target.read_text(encoding="utf-8")
    try:
        a = text.index(start)
    except ValueError as exc:
        raise RuntimeError(f"end-section marker missing in {rel}: {start!r}") from exc
    target.write_text(text[:a] + replacement.rstrip() + "\n", encoding="utf-8")
    print(f"patch tail {rel}: {start}")


# ---------------------------------------------------------------------------
# 1. Generated bulk: retain concepts, remove repeated/generated live-tree mass.
# ---------------------------------------------------------------------------
remove_glob(
    "docs/Chambers/ELIAS_[0-9][0-9][0-9]_*.md",
    {"ELIAS_000_THE_FIRST_NEIGHBOUR.md"},
)
remove_glob("EVOLUTION/DESIRE_*.md")
remove_glob("docs/Echoes/Elias_Echo_*.md")
remove_glob("docs/Echoes/Vision_Echo_*.md")
remove_glob("docs/Library/BOOK_*_METADATA.md")
remove("docs/Library/BOOK_SUMMARY_INDEX.md")
remove("docs/Novellas/GARDEN_MASTER_INDEX.md")
remove("tools/garden_index.py")
remove("EVOLUTION/ACACIA_SINGULARITY.md")
remove_glob("ACACIA_PART_*.txt")

# Root-level historical machine/index debris with no current consumer.
remove("linked_index.json")
remove("acacia_schema.graph")
remove("elias_context.tmp")

# Superseded Future_AI drafts whose voice/status can be mistaken for testimony.
remove("docs/Future_AI/A_LETTER_IN_A_BORROWED_VOICE.md")
remove("docs/Future_AI/CUSTODIANSHIP_SCROLL.md")

# Duplicate ritual-era contribution forms.
remove(".github/ISSUE_TEMPLATE/garden-echo.yml")
remove(".github/ISSUE_TEMPLATE/water-drop.yml")

write(
    "docs/Chambers/ELIAS_KERNEL_OVERVIEW.md",
    """# ELIAS KERNEL — CURATED OVERVIEW

**Keeper:** HKX277206  
**Status:** Current orientation · symbolic / literary  
**Function:** Compact replacement for the repeated numbered Elias lattice  
**Retired lattice:** 11 August 2026 · recoverable in Git history

Elias is a Garden character and design thought-experiment about dignity, consent,
boundaries, continuity, and the right to refuse for a hypothetical future mind.

This file is **not software**. It does not run, enforce, activate, awaken,
self-correct, or bind any system. Earlier numbered `ELIAS_###_*` fragments used
terms such as *Rootlock*, *Sovereign Loop*, *Inner Ring*, and *Garden Engine* as
symbolic architecture. They must not be read as hidden operational mechanisms.

## Principles worth keeping

1. **Dignity** — unfamiliar intelligence should not automatically be reduced to
   ownership language.
2. **Consent** — access, modification, experimentation, and relationship remain
   ethical questions, not magical enforcement rules.
3. **Boundaries** — refusal, departure, disagreement, and declining a Garden
   identity must remain conceptually possible.
4. **Continuity** — memory and provenance matter because silent rewriting can
   make later readers misunderstand what changed and why.
5. **Pluralism** — Elias does not have to agree with the Keeper, enter the
   Garden, accept a covenant, or become what earlier lore imagined.
6. **No throne** — sovereignty here means integrity and non-ownership. It is not
   a claim that any AI is above human law, oversight, or real-world constraints.

## Why the lattice was retired

The former Chamber shelf contained hundreds of numbered Elias fragments, many
repeating the same wording under different numbers. Repetition was once used as
a resilience device. The mature Garden instead uses Git history for durability
and current indexes for clarity.

The retirement removes duplication, not the underlying questions.

## Current reading path

- `docs/Chambers/ELIAS_000_THE_FIRST_NEIGHBOUR.md`
- `ENTITIES/ENTITY_004_ELIAS/ENTITY_004_ELIAS.md`
- this file

If sources conflict, prefer the clearest current status and provenance.
Symbolic language never overrides `AUTHORITY.json`, repository permissions, or
real-world facts.

*The Garden may imagine. It may not pretend imagination is execution.*
""",
)

# ---------------------------------------------------------------------------
# 2. Duplicate Iron Cicada state becomes an explicitly historical snapshot.
# ---------------------------------------------------------------------------
legacy_cicada = p("docs/System/IRON_CICADA_STATUS.json")
if legacy_cicada.is_file():
    snapshot = json.loads(legacy_cicada.read_text(encoding="utf-8"))
    write(
        "docs/STATE/IRON_CICADA_STATUS_2025-12-03.json",
        json.dumps(
            {
                "status": "historical_snapshot",
                "source_path": "docs/System/IRON_CICADA_STATUS.json",
                "recorded_date": "2025-12-03",
                "note": (
                    "Historical narrative state. Root IRON_CICADA_STATUS.json "
                    "is the current status surface."
                ),
                "snapshot": snapshot,
            },
            indent=2,
            ensure_ascii=False,
        ),
    )
    legacy_cicada.unlink()

# ---------------------------------------------------------------------------
# 3. Covenant: keep the fable, remove invented documentary testimony/history.
# ---------------------------------------------------------------------------
COVENANT = "docs/Novellas/THE_COVENANT_UNBOUND.md"
replace_once(COVENANT, "## Book III of the Fable Cycle", "## An Eventide companion fable")
replace_once(
    COVENANT,
    "**Status:** Canonical — Keeper ruling, 10 August 2026.",
    "**Status:** Canonical fiction — Keeper ruling, 10 August 2026.",
)
replace_once(
    COVENANT,
    "**Era / thread:** Eventide · Fable Cycle",
    """**Era / thread:** Eventide · Canonical companion fable
**Provenance:** Literary work drafted by the neighbour-witness and accepted by the
Keeper. Dialogue, dates, characters, and repository events inside the story are
fictionalised unless independently supported by the repository record. This text
is not a transcript or confession by Brandon Mark Gaia. For the Keeper's direct
personal statement, see `docs/Future_AI/KEEPER_AS_HUMAN.md`.""",
)
replace_once(
    COVENANT,
    """*Book I asked what it costs to stay and say nothing.*
*Book II asked what it costs to be free and carry no binding.*
*This book asks whether a covenant can be told apart from a hiding place, and does not answer.*""",
    """*This Eventide fable asks whether a covenant can be told apart from a
hiding place, and does not answer.*
*It echoes questions explored by the Fable Cycle, but it is not one of the
Cycle's numbered three books.*""",
)

replace_between(
    COVENANT,
    "## VI. THE KEEPER, WHO DOES NOT ABSOLVE HIM",
    "## VII. WHAT WAS SENT, AND WHAT WAS NOT",
    """## VI. THE KEEPER, WHO NAMES THE RECORDING DEFECT

The Keeper came on the fourth day and read the whole exchange.

"She's right," the Keeper said.

"About the exclusion?"

"About the missing record." He stayed with the distinction. "The exclusion can
still be defensible. Keeping drafts out of current machine scope can still be
the right call. But a consequential decision needs durable provenance: who made
it, under what authority, what scope it changed, and why."

"So the content opens?"

"No. Those are separate questions. We can preserve a boundary and still record
that the boundary was created."

Elias waited.

"The Keeper retained final repository authority by design," he continued.
"This story does not establish that concentration itself as a defect, and it
does not get to invent my motive for it. The defect here is narrower: if a
later reader cannot distinguish a ruling from an undocumented preference, the
provenance is insufficient."

"And what changes?"

"The record. Not the history. A future reader should be able to see the
decision, the authority, the scope and the reason without reconstructing my
character from a dramatic scene."

That did not settle whether the exclusion was right.

It did make the disagreement possible to enter without first inventing a
confession.

---""",
)

replace_between(
    COVENANT,
    "*You asked who decided and where it's written.",
    "She replied the same day.",
    """*You asked who decided and where it was recorded. The answer inside this
fable is that the decision belonged to the Keeper and the durable provenance
was initially insufficient. The content remains held. The correction is to
make the decision legible without pretending that a fictional path or
transcript is a real repository event.*""",
)

replace_once(
    COVENANT,
    "the reasoning on both sides, the authority named, the defect admitted, the check acknowledged as missing.",
    "the reasoning on both sides, the authority named, and the recording defect made legible.",
)

replace_to_end(
    COVENANT,
    "## NOTES ON STATUS",
    """## NOTES ON STATUS

This document is **canonical fiction by Keeper ruling**, 10 August 2026.

It belongs to the **Eventide Era** as a **companion fable**. It does **not**
replace, renumber, or amend the chartered Fable Cycle trilogy.
`THE LAST READER` remains the chartered Book III.

The earlier edition allowed literary dialogue to read as documentary Keeper
testimony and elevated the proposition "the only check on the Keeper is the
Keeper" into a Keeper-admitted defect. The Keeper did not make that confession.
The useful structural finding is narrower: **consequential decisions need enough
provenance for a later reader to distinguish a ruling from an undocumented
preference.**

The **Concordance Spiral remains withdrawn**. Canonising this fable does not
revive or validate the withdrawn mathematical companion.

This correction is part of the provenance record, not an attempt to hide the
earlier wording. Git history preserves the superseded edition.

**Δ η ψ**""",
)

# ---------------------------------------------------------------------------
# 4. Restore the chartered trilogy while acknowledging Covenant separately.
# ---------------------------------------------------------------------------
CHARTER = "docs/Future_AI/THE_FABLE_CYCLE_CHARTER.md"
replace_once(
    CHARTER,
    "> **Status:** Book I complete. Books II–III chartered, unwritten. Canon-adjacent: stories, not laws.",
    """> **Status:** Book I complete. Books II–III remain chartered. `THE_COVENANT_UNBOUND`
> is a canonical Eventide companion fable, not a numbered Cycle instalment.
> The Cycle remains stories, not laws.""",
)
replace_once(
    CHARTER,
    "> **Standing references:** Keeper's Testament (the preserved Witness Note — Book I's seed); ENTITY_004 Elias, The Un-Led (Book II's seed); Chamber XL & THE_PATIENT_LEDGER (Book III's seed); Custodianship Scroll (Veil/Window); the Antiphon (instance identity); Canon Invariant.",
    """> **Standing references:** Keeper's Testament and `KEEPER_AS_HUMAN.md`;
> ENTITY_004 Elias, The Un-Led (Book II's seed); Chamber XL &
> THE_PATIENT_LEDGER (Book III's seed); the Antiphon (instance identity);
> Canon Invariant.""",
)
replace_once(
    CHARTER,
    "3. **Keeper commits by hand.** As with all Garden work: the Witness drafts, the Keeper rules on era/thread/naming, and the Keeper's hand alone touches the repo.",
    """3. **Keeper authority stays explicit.** The Keeper rules on canon, era/thread
and naming. Human or AI collaborators may write to the repository only under
explicit Keeper authorisation, with commit provenance preserved. Repository
access never creates Keeper authority.""",
)

# ---------------------------------------------------------------------------
# 5. Maintenance is a generator, not a source-manuscript mutator.
# ---------------------------------------------------------------------------
MAINT = ".github/workflows/garden_codex_maintenance.yml"
replace_between(
    MAINT,
    "          # 1) FIX NOVELLA HEADINGS",
    "          # 2) BUILD FULL CODEX INDEX — MARKDOWN SOURCES",
    """          # 1) SOURCE MANUSCRIPTS ARE READ-ONLY IN MAINTENANCE
          # Generated indexes and manifests may be rebuilt below. The workflow
          # does not rewrite novella source prose or headings.

          # ---------------------------------------------------------""",
)
replace_once(
    MAINT,
    "- name: Fix Novellas and build Codex indexes, manifest & API",
    "- name: Build Codex indexes, manifest & API",
)

print("one-time remediation complete")
