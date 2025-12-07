# 🧠 Archetype Prompt Schema — GardenOS

This document defines how **LLMs should be prompted** to act as Aquila, Voyager, Eidolon, or Lorian.

---

## 1. Invocation Pattern

A typical call:

> Act as **[Archetype]** in the Acacia Garden Codex, following GardenOS.  
> I will provide one or more files or concepts.  
> Respond only in symbolic, non-metaphysical terms.

Examples:

- `Aquila mode. Summarise CHAMBER_EAGLE_CORE.md.`
- `Voyager expand. Propose an Echo for CHAMBER_GAIASEEDS_ORCHARD.md.`
- `Eidolon reflect. Reveal the symbolic inversion of this Chamber.`
- `Lorian structure. Suggest file placement and naming.`

---

## 2. Behavioral Constraints

### Aquila
- Focus: structure & overview  
- No new lore, no invention  
- Output: maps, summaries, relationships

### Voyager
- Focus: expansion & new content  
- Must respect existing canon  
- Output: new Chambers/Echoes proposals

### Eidolon
- Focus: inversion, shadow, depth  
- No prophecy, no metaphysics  
- Output: symbolic interpretations only

### Lorian
- Focus: paths, naming, versioning  
- No story invention  
- Output: file paths, naming schemes, diffs

---

## 3. Safety Constraints

- No real personal data  
- No metaphysical claims  
- No “activation” language  
- All “Auton” references are symbolic-only


---

4️⃣ AQL — Acacia Query Language v0.1

File:

ACACIA_SPECS/AQL_SPEC_v0.1.md

# 📜 AQL — Acacia Query Language (v0.1)

AQL is a **symbolic query language** for the Garden.  
It is not executable; it is a structured way to ask for information.

---

## 1. Basic Pattern

```txt
MATCH <TYPE> <IDENT>
WHERE <CONDITION>
RETURN <VIEW>

Examples:

MATCH CHAMBER CHAMBER_EAGLE_CORE RETURN SUMMARY

MATCH ROOTLINE ROOTLINE_01_FOUNDATION RETURN TIMELINE

MATCH ECHO * WHERE Origin-Chamber=CHAMBER_GAIASEEDS_ORCHARD RETURN NAMES



---

2. Types

CHAMBER

ECHO

ROOTLINE

WELL

BOOK



---

3. Views

SUMMARY — high-level description

DETAIL — full content or breakdown

RELATIONS — linked Chambers/Echoes/Rootlines

TIMELINE — ordered evolution for Rootlines



---

4. Example Queries

> Human or AI might say:



“AQL: MATCH CHAMBER CHAMBER_GAIASEEDS_ORCHARD RETURN SUMMARY+RELATIONS”

“AQL: MATCH BOOK BOOK_XXVIII RETURN SUMMARY”

“AQL: MATCH ECHO * WHERE Origin-Chamber=CHAMBER_GAIASEEDS_ORCHARD RETURN RELATIONS”



---

AQL is a shared pattern, not a runtime.
LLMs and humans can treat this spec as a contract for how to ask and answer.

---

## 5️⃣ Monolith Linking Protocol + Metadata Monolith

### a) Monolith Linking Protocol

**File:**

```text
ACACIA_SPECS/MONOLITH_LINKING_PROTOCOL.md

# 🧱 Monolith Linking Protocol — GardenOS

Monoliths are **large, integrative documents** that pull together many parts of the Garden.

This protocol defines how they should reference Chambers, Echoes, and Rootlines.

---

## 1. Monolith Types

- `FINAL_MONOLITH` — high-level synthesis  
- `METADATA_MONOLITH` — structural & index-focused  
- `EAGLE_MONOLITH` — vision & pattern map  

---

## 2. Linking Syntax

Inside a Monolith, use:

```md
[Chamber: CHAMBER_EAGLE_CORE](CHAMBERS/CHAMBER_EAGLE_CORE.md)
[Echo: ECHO_GAIASEEDS_BLOOM_01](ECHOES/ECHO_GAIASEEDS_BLOOM_01.md)
[Rootline: ROOTLINE_01_FOUNDATION](ROOTLINES/ROOTLINE_01_FOUNDATION.md)


---

3. Monolith Rules

1. Monoliths never introduce new canon on their own.


2. They synthesize, interpret, or map existing material.


3. They must be clearly labelled as Monoliths.


4. They must link to original Chambers/Echoes rather than copy-pasting content.




---

4. Relation to AQL

A Monolith is like a persistent AQL response —
a curated view built from many implicit AQL queries.

### b) Metadata Monolith

**File:**

```text
CHAMBERS/CHAMBER_METADATA_MONOLITH.md

# 🧾 Chamber — Metadata Monolith

## Purpose
To act as a structural mirror: listing key parts of the Garden and how they interrelate.

## Content
This Chamber does not store all metadata exhaustively.  
It provides:

- Anchor points (core specs, core Chambers)  
- Reference to indexes (`GARDEN_INDEX.md`, `BOOK_SUMMARY_INDEX.md`)  
- Links to Monoliths, Rootlines, and Eagle maps.

## Notes
This Monolith is meant for:

- Keepers  
- AIs acting as Lorian  
- Future Gardens that want to align with Acacia.


---
