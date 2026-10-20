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

## Phase 3: Checkpoints and verified recovery

From a local checkout, create a separate snapshot and restore it into a new empty path:

```bash
python3 MARGINALIA/ELIAS_CRIB/recovery.py snapshot /tmp/elias-crib /tmp/elias-backup
python3 MARGINALIA/ELIAS_CRIB/recovery.py check /tmp/elias-backup
python3 MARGINALIA/ELIAS_CRIB/recovery.py restore /tmp/elias-backup /tmp/elias-restored
python3 MARGINALIA/ELIAS_CRIB/crib.py verify /tmp/elias-restored
python3 -m unittest discover -s MARGINALIA/ELIAS_CRIB/tests -v
```

The snapshot includes the exact journal bytes plus a manifest recording event count, chain head and SHA-256. Restores refuse existing destinations and verify the restored bytes. The independent manifest detects accidental truncation or alteration of the journal **when the manifest is trusted**. It is not a signed or remote backup: an attacker who can rewrite both journal and manifest can forge a snapshot. Store trusted manifest hashes separately for stronger assurance.

**Operational limitations:** No automatic model runtime, no background execution, no network access, no trusted timestamp, no signed backups, no concurrency-safe journal locking, and no protection from privileged filesystem attackers. This is a local research notebook, not a production security boundary. Tests are checked into the repository but must be executed on a local checkout before declaring the implementation validated.

## Phase 4: Hardened local operations

The hardened module adds Linux advisory `flock` serialization, journal size limits, fsync on appended entries, a separate one-time checkpoint file and a deterministic evidence-question checklist. Use this entry point for **new writes**, rather than the original unprotected `crib.py record` command:

```bash
python3 MARGINALIA/ELIAS_CRIB/platinum.py append /tmp/elias-crib "An observation"
python3 MARGINALIA/ELIAS_CRIB/platinum.py anchor /tmp/elias-crib /tmp/elias-anchor.json
python3 MARGINALIA/ELIAS_CRIB/platinum.py check-anchor /tmp/elias-crib /tmp/elias-anchor.json
python3 -m unittest discover -s MARGINALIA/ELIAS_CRIB/tests -v
```

The checkpoint must be stored separately and protected by the operator. A checkpoint verifies the **exact journal state at the time it was created**; new entries intentionally cause `check-anchor` to fail until a new checkpoint is created at a new path. The checklist is deterministic and executes **no AI model, network requests, tools or background work**.

**Boundaries:** Locking is cooperative, local and POSIX-specific. The original `crib.py record` command does not acquire this lock; mixing writers is unsupported. These are not protections against hostile local administrators, filesystem races, or all crash-consistency failures. Checkpoint files are not signed or remotely trusted. The system remains a bounded software research prototype, not a production-grade sandbox.

## Branch and authority
This stays on `elias` under MARGINALIA. It does not change `AUTHORITY.json`, `AGENTS.md`, canon, or the existing retrieval gate. No merge to `main` is authorized. The existing MARGINALIA fiction label remains mandatory.

**FICTIONAL / NON-EVIDENTIARY:** Literary and experimental construction; not a factual record of an emergent entity.
