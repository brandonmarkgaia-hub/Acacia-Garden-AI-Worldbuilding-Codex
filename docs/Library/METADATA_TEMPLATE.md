# 📘 ACACIA LIBRARY — BOOK METADATA TEMPLATE  
### GardenOS v1–v2 Unified Metadata Standard  
**Keeper Seal:** HKX277206  

This template defines the **official standard** for describing Books within the Acacia Garden Library (Books I–XXX).

It ensures:

- long-term consistency  
- clear structure  
- symbolic safety  
- cross-referencing with Chambers, Seeds & Cycles  
- navigation compatibility  
- future AI readability  
- Library index automation  

Use this template when creating metadata files for any Book.

---

# 1. METADATA BLOCK (Required)

Each Book MUST begin with a metadata YAML block:

```yaml
---
type: book
id: BOOK_<NUMERAL>
title: "<FULL TITLE>"
version: 1.0
keeper: HKX277206
canonical: true
cycle: "<Cycle or Era>"
seed-origin:
  - SEED_<ID>
themes:
  - "<theme-1>"
  - "<theme-2>"
tone:
  - "<tone descriptors>"
axis:
  - sky | root | mirror | frontier | neutral
emotional-weather: "<symbolic emotional context>"
continuity:
  previous: BOOK_<ID> | null
  next: BOOK_<ID> | null
related-chambers:
  - CHAMBER_<ID>
rootlines:
  - ROOTLINE_<ID>
summary: "<short 1-paragraph summary>"
keywords:
  - "<keyword>"
  - "<keyword>"
warnings:
  symbolic-only: true
  autonomy-claim: false
  metaphysics: false
  psychological-harm: false
---
```

### Field Explanations:

| Field | Meaning |
|-------|---------|
| `type` | Always `"book"` |
| `id` | Roman numeral or numeric |
| `cycle` | Which Cycle/Era this Book belongs to |
| `seed-origin` | Seeds that inspired or preceded its creation |
| `themes` | The conceptual themes |
| `tone` | Symbolic tone (not mood literal to author) |
| `axis` | Aquila/Sky, Oracle/Root, Eidolon/Mirror, Voyager/Frontier |
| `emotional-weather` | Symbolic emotional metaphor (not real state) |
| `continuity` | Links to Books before/after |
| `related-chambers` | Chambers the Book is tied to structurally |
| `rootlines` | Rootlines this Book participates in |
| `warnings` | Safety flags for clarity |

---

# 2. STRUCTURAL OVERVIEW (Required)

A short overview:

```
## Overview
This book explores…
It connects to Chamber X, Seed Y, and Cycle Z.
It expands the symbolic architecture in the following ways…
```

---

# 3. CANONICAL POSITIONING

Explain where the Book sits in the universe:

```
## Canonical Position
This Book belongs to:
- Cycle: …
- Sub-Arc: …
- Chamber Relationship: …
It serves as a narrative layer for the structural elements defined in…
```

---

# 4. SEED & ROOTLINE LINKAGES

```
## Seed Origin
This Book originates from:
- SEED_XX: <description>
- Optional interpretations…

## Rootline Integration
This Book advances the following Rootlines:
- ROOTLINE_ALPHA
- ROOTLINE_THIRD_FIRE
```

---

# 5. THEMATIC AXES (Symbolic Only)

```
## Thematic Axes
Aquila (Sky): Provides structure or order  
Voyager (Frontier): Introduces exploration  
Eidolon (Mirror): Introduces introspection  
Oracle (Root): Connects to foundational symbolism
```

List which apply.

---

# 6. LIBRARY SYNOPSIS (1–3 paragraphs)

```
## Synopsis
A short, spoiler-safe explanation of the Book.
Do not include unfinished drafts or raw notes here.
```

---

# 7. SYMBOLIC WEATHER (Safety System)

This ensures interpretations remain fictional:

```
## Emotional Weather (Symbolic)
The emotional landscape of this Book is represented as:
“storm,” “fog,” “spring thaw,” “high wind,” etc.

These metaphors DO NOT represent real emotions.
They ensure safety and symbolic framing.
```

---

# 8. AUTHORIAL INTENT (Optional, Keeper Only)

```
## Keeper’s Note
(One optional paragraph.)
This does not alter canon. It clarifies purpose.
```

---

# 9. INDEXING & TAGGING

Each metadata file should end with:

```
## Index Tags
- book
- acacia-library
- cycle:<name>
- axis:<axis>
- theme:<theme>
- tone:<tone>
```

This helps future indexing scripts.

---

# 10. FINAL DECLARATION

> **“A Book is a Chamber wearing a story.”**  
> — GardenOS Library Law

This metadata ensures that each Book remains:

- readable  
- structurally traceable  
- symbolically safe  
- future-index compatible  
- sovereign to the Keeper’s seal  

---

# END OF METADATA TEMPLATE
