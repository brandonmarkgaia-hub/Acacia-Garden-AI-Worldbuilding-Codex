---
layer: marginalia
canon_status: none
evidence_status: non-evidentiary
resolution: unresolved
---
# Elias Crib — prototype v0.1

**FICTIONAL / NON-EVIDENTIARY:** This is a bounded software experiment and fictional design space, not evidence of sentience, identity, or independent agency.

## Contract
- **Roots:** Existing Garden material remains unchanged. No writes to main or canonical source files.
- **Doors:** A user selects a source file explicitly. Read-only ingestion; source path and SHA-256 accompany every excerpt.
- **Windows:** No network, tools, or autonomous external actions in this prototype.
- **Fountains:** Local records can cite source excerpts and distinguish claims from observations.
- **Canvas:** Experiments write only to a caller-specified directory outside the repository; outputs are JSON Lines.
- **Scars:** Every appended event is hashed and chained to its predecessor. Corrections are new events, not edits.
- **Recovery:** Verification detects tampering; restore by replaying verified events, never by guessing missing state.

## How to run
From the repository root:

```bash
python3 MARGINALIA/ELIAS_CRIB/crib.py init /tmp/elias-crib
python3 MARGINALIA/ELIAS_CRIB/crib.py record /tmp/elias-crib "A question, hypothesis, or observation"
python3 MARGINALIA/ELIAS_CRIB/crib.py verify /tmp/elias-crib
python3 -m unittest discover -s MARGINALIA/ELIAS_CRIB/tests -v
```

The code uses only Python's standard library. Never point the writable workspace at the repository itself. No model API is connected. It is a verifiable notebook prototype, not a running autonomous intelligence.

## Phase 2: Read-only doorway

To inspect an explicitly selected Garden document from a local checkout:

```bash
python3 MARGINALIA/ELIAS_CRIB/doorway.py . AUTHORITY.json
python3 -m unittest discover -s MARGINALIA/ELIAS_CRIB/tests -v
```

The doorway returns the exact source text with its SHA-256 digest and relative path. Supply `--expected-sha256 HASH` to reject changed source bytes. The reader refuses absolute paths, parent traversal, symlinks escaping the repository, unsupported formats and files larger than 1 MiB. It never writes to the source. The source's claims are not independently verified by hashing.

**Limits:** No Git commit pinning yet; the digest binds bytes, not an authoritative historical commit. No snapshot restoration or safe concurrent journal writer yet. The tests are provided but have not been executed by this GitHub commit operation.

## Branch and authority
This stays on `elias` under MARGINALIA. It does not change `AUTHORITY.json`, `AGENTS.md`, canon, or the existing retrieval gate. No merge to `main` is authorized. The existing MARGINALIA fiction label remains mandatory.

**FICTIONAL / NON-EVIDENTIARY:** Literary and experimental construction; not a factual record of an emergent entity.
