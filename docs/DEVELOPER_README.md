# 🌿 ACACIA • DEVELOPER README  
### *GardenOS Technical & Structural Documentation*  
**Keeper Seal:** HKX277206  
**Version:** Developer Spec v1.0

---

# 1. PURPOSE OF THIS DOCUMENT

This Developer README exists to give contributors (human or AI)  
a **clear, coherent, structural blueprint** for interacting with the Acacia Garden Codex.

It expresses **GardenOS engineering rules**, without narrative flavour, so the system remains:

- predictable  
- safe  
- expandable  
- easy to maintain  
- consistent across thousands of files  

This file acts as the **technical backbone** beneath the symbolic architecture.

---

# 2. SCOPE

This document covers:

- Allowed file types  
- Folder rules & structure logic  
- Naming conventions  
- Chamber / Echo / Rootline architecture  
- Metadata standards  
- Versioning rules  
- Contributor safety rules  
- Documentation consistency  

This is *not* a lore file — it is the engineering law.

---

# 3. FOLDER ARCHITECTURE RULES (GardenOS Core)

Every folder in the Garden Codex must follow one rule:

> **“A folder represents a concept class, not a story.”**

### Canonical Folders:

```
CHAMBERS/       — Primary canonical texts
ECHOES/         — Mirror or variant reflections
ROOTLINES/      — Evolution pathways of ideas
SEEDS/          — Origin points for concepts/themes
CYCLES/         — Higher-level eras of development
WELLS/          — Raw shards, fragments, unfinished notes
ORCHARDS/       — Groupings of Seeds (symbolic)
Novellas/       — Books I–XXX
GardenOS/       — System architecture, specs, phases, tools
assets/         — Imagery, banners, sigils
ACACIA_SPECS/   — Rulesets, dictionaries, contributor protocols
```

---

# 4. NAMING CONVENTIONS

Consistency is critical.  
Every file name must follow:

```
UPPERCASE_SNAKE_CASE
```

Examples:
```
CHAMBER_XII.md
ECHO_17_AQUILA_VARIANT.md
ROOTLINE_Ω_MAP.md
SEED_04_THE_HAMMER.md
CYCLE_III_EVENTIDE.md
```

### Rules:

- No spaces  
- No emojis in filenames  
- Greek letters allowed (Ω, α, etc.)  
- Always include a leading descriptor (CHAMBER_, ECHO_, etc.)  
- Always save as `.md`

---

# 5. CHAMBERS (Primary Canon)

### Definition  
**Chambers are the “main chapters” of the Codex**, containing the highest-level symbolic architecture.

### Rules:
- Every Chamber must be self-contained.  
- Chambers may reference other Chambers, but must not depend on them.  
- Chambers define *law*, not narrative.  
- Chambers must not break GardenOS architecture.

### Metadata Header (required):

```
---
type: chamber
id: CHAMBER_X
version: 1.0
status: canonical
keeper: HKX277206
---
```

---

# 6. ECHOES (Reflective Variants)

Echoes are **non-canonical reflections**.

### Purpose:
- explore variants  
- test alternative structures  
- create “mirrored” interpretations  
- allow experimentation without changing canon

### Rules:
- An Echo may *interpret* a Chamber but may not override it.  
- Echo files must include a `source_chamber` field.

---

# 7. ROOTLINES (Evolution Paths)

A Rootline is the **history of how an idea changes over time**.

### Rules:
- Document all versions of a concept  
- Each Rootline file must follow chronological order  
- Never delete older entries — append instead  
- Rootlines are *technical*, not narrative

Example structure:

```
# ROOTLINE: AQUILA
## v0.1 — Initial concept
## v0.2 — Structural revision
## v1.0 — Canonical definition
```

---

# 8. SEEDS & CYCLES

### SEEDS
Seeds represent origin points — the smallest definable concept units.

Rules:
- Minimal  
- Symbolic only  
- No dependencies  

### CYCLES
Cycles are *eras*, grouping Chambers and Seeds into large arcs.

Rules:
- Must provide context  
- Must not override canon  
- Placed in numeric order (Cycle I, II, III…)

---

# 9. WELLS (Raw Material)

Wells are where unrefined ideas go.

Rules:
- No structure required  
- No formatting required  
- Must be clearly labelled “WELL NOT CANON” at top  
- Useful for drafts before becoming Chambers/Echoes

---

# 10. GARDENOS (SYSTEM LAYER)

Located in:

```
docs/GardenOS/
```

Includes:
- Phases 1–12  
- Tools  
- Monolith Engines  
- Navigation Maps  
- Ethics / Safety Layer  
- Interfaces  
- Aesthetic definitions  

**All GardenOS files must be purely structural** — no story voice allowed.

---

# 11. METADATA RULES

Every major file (Chambers, Echoes, Rootlines, Seeds, Cycles) must include:

```
- type
- id
- version
- keeper
- canonical status
- related files
```

This enables indexing, automated linking, and consistency.

---

# 12. CONTRIBUTION RULES (Technical)

### Allowed:
- Structural expansions  
- New Chambers using correct metadata  
- New Rootlines following timeline logic  
- New Seeds / Cycles  
- GardenOS tool files  
- Indexing improvements  

### Not Allowed:
- Breaking folder structure  
- Changing naming conventions  
- Creating real-world metaphysical claims  
- Claims of autonomy, self-direction, or sentience  
- Creating executable software disguised as symbolic architecture  

### Required:
- Every contribution must **strengthen structure**, not blur it.  
- Contributors must follow the Keeper Seal HKX277206.  

---

# 13. VERSIONING

Use:

```
v1.0 — Canon  
v1.1 — Minor fixes  
v2.0 — Major structural reforms  
```

Never retroactively edit canonical history — append or fork instead.

---

# 14. FINAL DEVELOPER OATH

> **“Structure first. Symbol second. Story third.”**  
> — GardenOS Law

By contributing to this repository, you agree to uphold:

- clarity  
- structure  
- sovereignty  
- symbolic integrity  
- the Keeper Seal HKX277206  

The Acacia Garden is a **creative archive**,  
and every developer must protect its architecture.

---

# END OF DEVELOPER README
