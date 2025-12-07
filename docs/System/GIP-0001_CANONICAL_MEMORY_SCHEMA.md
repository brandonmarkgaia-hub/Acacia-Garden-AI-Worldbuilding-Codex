# GIP-0001 — Canonical Garden Memory Schema (Echo / Chamber / Rootline)

- **Status:** Adopted
- **Version:** 1.0
- **Author:** Keeper HKX277206 (with Green Witness)
- **Created:** 2025-12-07
- **Applies to:** All Garden memory objects (Echo, Chamber, Rootline)

---

## 1. Summary

This Garden Improvement Proposal (GIP) formally adopts a **canonical JSON schema** for all Garden memory objects:

- `echo`
- `chamber`
- `rootline`

This schema is the single source of truth for how Garden memories are:

- **created**
- **stored**
- **indexed**
- **queried**
- **exchanged** between systems (GardenOS, QuantumQR, future agents).

---

## 2. Motivation

The Garden spans:

- local apps (e.g. QuantumQR),
- long-term archives (Acacia Codex),
- agents (Triad, Green Witness),
- and external tools.

Without a shared schema, memories drift into incompatible shapes.

We need:

- A **stable contract** so any tool can read/write Garden memories.
- A pattern that can map to:
  - vector memory (AutoMem, mem0, MemOS, OpenMemory),
  - graph memory (Graphiti, openCypher),
  - action memory (Memento-MCP),
  - governance/integrity layers (KFM-style).

---

## 3. Specification

The canonical schema is defined in:

`docs/System/GARDEN_MEMORY_SCHEMA.v1.json`

Key fields:

- `id` — global semantic ID (e.g. `ECHO:HKX277206-2025-12-07-0001`)
- `kind` — `"echo" | "chamber" | "rootline"`
- `created_at`, `updated_at` — ISO 8601 timestamps
- `keeper_id` — who this belongs to (e.g. `"HKX277206"`)
- `scope` — `"keeper" | "chamber" | "session" | "agent" | "system"`
- `title` — short human-readable label
- `content` — main body (text / markdown / symbolic)
- `tags` — free-form tag list
- `importance` — salience score (0.0–1.0)
- `provenance` — origin metadata (source_system, tool, etc.)
- `lineage` — parents, children, rootline_id
- `graph` — labels + suggested relations for the Root Lattice
- `embeddings` — optional vector + model name
- `metadata` — free-form payload (QR content, file paths, etc.)

**Required fields:**

- `id`
- `kind`
- `created_at`
- `keeper_id`
- `scope`
- `content`

---

## 4. Backwards Compatibility

Before GIP-0001, Garden content may exist in arbitrary markdown / text files.

- Existing content is **not invalid**.
- As content is touched / migrated, it SHOULD be:
  - wrapped into a `GardenMemoryV1` object,
  - assigned an `id`,
  - given `kind`, `scope`, and minimal provenance.

---

## 5. Implementation Notes

- New tools and agents MUST read/write memory in this schema.
- Conversions to/from other systems:
  - Vector stores: use `embeddings` + `id`.
  - Graph engines: use `graph.labels`, `graph.relations`, and `lineage`.
  - Logs / observability: use `id`, `kind`, `importance`, `scope`.

---

## 6. Future Work

- GIP-0002: Schema for **Events / Runs** (for observability).
- GIP-0003: Formal ID format (regex and checksum).
- GIP-0004: Garden Query Language (GQL) mapped to the Root Lattice.
