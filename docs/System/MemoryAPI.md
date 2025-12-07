# Garden Memory API (Developer Notes)

This document describes a **thin, language-agnostic API** for working with Garden memories
following `GARDEN_MEMORY_SCHEMA.v1.json`.

It is intentionally simple so it can be implemented in:

- Python
- Kotlin/Android (QuantumQR)
- JS/TS (Eidolon UI)
- Any future stack

---

## 1. Core Operations

### 1.1 Create Memory

```pseudo
GardenMemory create_memory(GardenMemory input)
