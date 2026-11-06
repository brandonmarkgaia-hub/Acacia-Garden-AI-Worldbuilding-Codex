# Cull decision review — 2026-11-06

**Static classification only; no source files changed.**

Inspection of the supplied Claude `cull.sh` found 242 distinct operations:
- **181 archive candidates** (all `q` commands). Preserve content and provenance; prove actual retrieval/index exclusions and repair inbound links before moving.
- **23 mutation duplicate deletion candidates** (`MUTATIONS/MUTATION_*`). Recheck byte-for-byte equality against the surviving twin on current main before deletion.
- **38 other deletion candidates** (Echo Chronicle, Chamber, Library summaries, novella and Lost Epoch). These require individual content and inbound-reference review. Do not automatically delete them.

The original proposal's 16-character hash prefixes are insufficient as a full SHA-256 ledger. The proposed script skips missing files and checks dependencies too late.

**Release gate:** full 64-character SHA-256 ledger; source/destination verification; reviewed 38 deletion decisions; links and redirects; retrieval exclusion test; reproducible index rebuild; Gatekeeper and CI success. No cull or merge is authorized by this report.

Local path-by-path CSV was generated from the original uploaded script; it has not been committed because the script and attachment are not accessible to the GitHub connector as a repository file.
