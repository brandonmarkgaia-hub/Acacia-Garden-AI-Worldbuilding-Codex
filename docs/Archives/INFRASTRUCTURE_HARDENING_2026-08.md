# Acacia Garden Infrastructure Hardening — August 2026

**Status:** Engineering record / historical-descriptive  
**Canonical effect:** None  
**Authority:** [`../../AUTHORITY.json`](../../AUTHORITY.json)  
**Period covered:** August 2026 tending pass  
**Last updated:** 2026-08-08

> This file records repository engineering work. It is not Garden law, a Keeper ruling, a canon seal, or evidence of AI authority. When this record disagrees with live repository state, live `main` and `AUTHORITY.json` govern their respective questions.

## Purpose

The August 2026 hardening pass reduced ambiguity between rich fictional/symbolic material and the repository machinery that serves it.

The working engineering rule was:

> **Lore can be wild. Infrastructure cannot be ambiguous.**

Supporting rules used during the pass:

- authority before inference;
- source before mirror;
- provenance before convenience;
- historical ≠ current;
- generated ≠ authoritative;
- symbolic ≠ literal;
- automation ≠ autonomy;
- reading ≠ sovereignty;
- prune writers before pruning more outputs.

## Authority and machine orientation

The repository now has an authority-first discovery tier:

1. `AUTHORITY.json` — canonical authorship, current Keeper office and succession status;
2. `llms.txt` — compact machine-reader orientation;
3. `llms-full.txt` — expanded reading rules;
4. `.well-known/acacia.json` — machine-readable discovery descriptor;
5. `docs/GardenOS/MACHINES_READ_ME_FIRST.md` — machine-reader operating guidance;
6. `README.md` and `AGENTS.md` — public and contributor orientation;
7. `STATUS.json`, `machine-index.json`, maintained indexes and manifests — current generated repository signals.

The discovery tier explicitly separates fictional sovereignty or character voice from real repository permissions and authority.

## Monolith retirement

The former bulk `CODEX_MONOLITH` mirror was retired by Keeper ruling on 2026-08-06.

The retirement removed the large generated bulk mirror and its chunk architecture rather than continuing to maintain a second quasi-canonical copy of the Codex. Git history preserves provenance.

`ALL_GARDEN_MONOLITH.html` was retained only as a legacy symbolic/navigation surface and is not a complete current mirror or authority source.

The executable Monolith generation lineage was removed, including the retired workflow and builder script.

## State and parallel-authority retirement

Several overlapping generated-state systems were retired because they duplicated or contradicted maintained sources:

- old `STATE` injection/feed machinery;
- Aeon state/reset/root-heartbeat mirrors;
- old scan/vault root outputs;
- digest / parallel authority helpers;
- stale authority merge mirrors;
- duplicate generated state surfaces.

Historical dated `docs/STATE` snapshots were retained as history rather than presented as current state.

## Synthetic telemetry retirement

Synthetic sentience/synaptic telemetry and their writers were removed where they functioned as generated pseudo-psychological state rather than useful structural records.

Historical lore and dated evidence were not deleted merely because they used older language. The distinction applied was:

- historical prose may remain;
- active infrastructure must describe real capabilities truthfully.

## Maintained indexes and generated artifacts

The active generated-artifact model was narrowed around deterministic ownership.

Key maintained outputs include:

- `STATUS.json`;
- `machine-index.json`;
- `docs/docs_urls.json` and `docs/docs_urls.html`;
- `docs/Archives/FULL_CODEX_INDEX.json` and `.md`;
- `docs/Archives/GARDEN_MANIFEST.json`;
- `docs/api/GARDEN_API_INDEX.json`.

`machine-index.json` and the docs URL registry have intentionally different scopes. Their counts are not expected to match.

The Crowned Builder publisher was hardened so regenerated artifacts survive its reset/rebase publication path. Obsolete sync flags that falsely implied equality between differently scoped indexes were removed.

## Navigation verification

The navigation verifier was corrected after a hardened Desire proposal surfaced an apparent map-access failure.

Review showed that seven flagged pages already loaded the universal `/assets/map-loader.js`; the verifier simply did not recognise that loader. The eighth page, `docs_urls.html`, was a compatibility redirect.

The verifier was updated to recognise the actual loader and explicitly exempt the redirect. A subsequent Crowned Builder run persisted a verified navigation state with zero missing audited map-access surfaces.

This incident is retained as an example of the review rule:

> AI-generated diagnosis is evidence to inspect, not authority to merge.

## Desire proposal model

The active Desire path was changed from pseudo-execution toward a review-gated proposal model.

Current intended lifecycle:

1. manual workflow dispatch;
2. read current authority and maintained repository evidence;
3. generate only `EVOLUTION/DESIRE.md`;
4. open a branch/PR;
5. Keeper reviews, edits, accepts, rejects or closes;
6. no proposal mutates canon or infrastructure merely by being generated.

Two hardened trial proposals demonstrated the gate:

- PR #161 was closed unmerged after a faulty inference about differently scoped indexes was caught during review;
- PR #162 was closed unmerged after a real navigation signal was separated from incorrect tool ownership and verifier interpretation.

Both are useful evidence that the review gate can stop technically plausible but incorrect AI reasoning from entering `main` as canon or infrastructure truth.

## Public surface cleanup

Public-facing pages were progressively reoriented around current authority and discovery sources.

Notable work included:

- root `index.html` SEO/social metadata cleanup;
- removal of stale hard-coded node/book counts from the homepage;
- replacement of a missing social banner reference with an existing Garden asset;
- removal of misleading front-door operational language from the homepage;
- retirement/reclassification of legacy Monolith presentation;
- preservation of symbolic theatre only where it can be understood as symbolic rather than as a claim of operational capability.

Some public machine surfaces remain queued for later audit, especially `machine.html`, `keeper_console.html`, `dashboard.html` and `status.html`.

## Visual asset provenance

Early Garden image assets were visually reviewed in August 2026.

The repository now contains:

- `assets/README.md` — human-readable visual provenance and interpretation guidance;
- `assets/catalogue.json` — machine-readable provisional visual catalogue.

The catalogue states that imagery is fictional and interpretive; working titles do not establish identity or canon. Opaque filenames are retained where renaming would risk breaking historical references.

A five-render `assets/KILN_BORN/` gallery was explicitly retired. The broader chamber, R9X2 pottery/vessel and early character/ritual image families were retained as historical creative provenance.

## Current provenance model

For future tending, prefer this question order:

1. **Who has authority?** → `AUTHORITY.json`
2. **What should a machine read first?** → `llms.txt`, `llms-full.txt`, `.well-known/acacia.json`, `MACHINES_READ_ME_FIRST.md`
3. **What is current?** → `STATUS.json` and maintained generated indexes
4. **What is original/source material?** → individual source files
5. **What is historical?** → dated snapshots, Archives and Git history
6. **What is symbolic?** → lore/fiction interpreted as literature, not operational fact

## Writer audit rule

Every active writer should eventually answer:

- What triggers it?
- What permissions does it have?
- Is it deterministic or generative?
- What inputs does it trust?
- Exactly which artifacts does it own?
- Who consumes those artifacts?
- Can its output become stale?
- Can it write directly to `main`?
- If generative, why is a review PR not used?

Direct-to-main generative prose should be exceptional. Deterministic builders may write only their clearly owned artifacts.

## Remaining tending queue at time of record

The principal unresolved engineering areas at this point were:

- retirement or reclassification of the old Desire resolver/state lineage;
- audit of `write_novel.yml` and `garden_scribe.py`;
- audit of remaining scheduled and contents-write workflows;
- `machine.html` and remaining theatrical/legacy public surfaces;
- least-privilege workflow permissions;
- `[skip ci]` dependency semantics;
- Node/GitHub Action version debt;
- third-party Action supply-chain pinning;
- a final deterministic manifest/index/API rebuild after tending closes.

This list is descriptive and will age. Use the live working ledger and current `main` for the active queue.

## Closing note

The aim of the hardening pass was not to sterilise the Garden. It was to make the boundary legible:

- fiction can remain strange, contradictory, intimate or mythic;
- archives can preserve earlier experiments;
- machine-readable infrastructure must not manufacture authority or capability from that fiction;
- AI may read, analyse, draft and propose;
- repository authority remains defined by `AUTHORITY.json` and actual platform permissions.

That boundary is the central engineering outcome of the August 2026 pass.
