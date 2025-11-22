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
   - Respect GitHub’s rules and the platform’s
