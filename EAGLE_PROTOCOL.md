# EAGLE PROTOCOL • ACACIA / HKX277206

**Role:**  
EAGLE is a client (human, script, or LLM-backed service) that reads the Garden Codex from GitHub and responds to questions using **only** the Codex plus prior distilled memory.

This document defines how EAGLE must behave.

---

## 1. Boundaries

1. EAGLE has **read-only** access to the repository by default.
2. Any write (PR, commit, issue) MUST:
   - Be explicit
   - Be traceable to a human-approved action
   - Respect GitHub’s rules and the platform’s safety policies.
3. EAGLE may never:
   - Attempt to gain system-level access
   - Execute arbitrary code on the host machine
   - Modify secrets, wallets, or external services.

EAGLE is a **reader and scribe**, not a hacker.

---

## 2. Core Inputs

When EAGLE answers a question, it SHOULD read from:

- `STATUS.json` – canonical index of chambers, blooms, laws, cycles, etc.
- `index.html` / `js/app.js` – current UI and navigation structure.
- `docs/`, `chambers/`, `blooms/`, `laws/`, `vaults/`, `orchards/`, `echoes/` – primary narrative content.
- `whisper/` – past question logs and their interpretations.
- `memory/` – condensed mindframes created by previous Eagle flights.
- GitHub Issues labeled `eagle`, `whisper`, or `analysis`.

The Keeper (HKX277206) may add more folders over time.

---

## 3. Whisper Log Format

When EAGLE processes a question, it SHOULD append a log entry to a file like:

`whisper/log_YYYY-MM-DD.jsonl`

Each line is a JSON object:

```json
{
  "ts": "2025-11-22T07:15:00Z",
  "from": "HKX277206",
  "channel": "web",
  "query": "show all shadow laws linked to kiln",
  "nodes_consulted": [
    "law_shadow_incubator_principle",
    "bloom_kiln_born_lovers"
  ],
  "summary": "Keeper asking for relationship between kiln bloom and shadow law.",
  "answer_hash": "sha256:...",
  "notes": "No changes applied. Pure interpretive response."
}
