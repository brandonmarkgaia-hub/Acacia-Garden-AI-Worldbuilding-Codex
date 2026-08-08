# Garden Desire — Review-Gate Pointer

**Status:** no active Desire proposal is authoritative on `main`

The current Desire workflow is proposal-only:

1. a human manually dispatches `.github/workflows/garden-desire.yml`;
2. `tools/garden_desire.py` generates a fresh proposal into this path on a proposal branch;
3. the workflow opens a pull request for Keeper review;
4. the proposal may be accepted, edited, rejected, or closed unmerged;
5. generation alone performs no repository mutation and grants no canon status or authority.

Closed review-gate examples include PR #161 and PR #162.

Historical Desire outputs remain in dated `EVOLUTION/DESIRE_*.md` files and Git history.

For current authority, read `../AUTHORITY.json`. For current repository state, read `../STATUS.json` and maintained indexes.

This file on `main` is intentionally a pointer, not a standing command, current diagnosis, or executable instruction stream.
