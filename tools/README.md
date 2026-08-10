# Current Garden Tools

`tools/` is the **current workshop**, not a historical dumping ground. Files here should have an identifiable current purpose or consumer.

Current executable tools:

- `garden_lore_helper.py` — deterministic STATUS and owned-index preparation for Crowned Builder.
- `garden_verify.py` — deterministic navigation/index verification written into `STATUS.json`.
- `garden_desire.py` — manual proposal generator; output is review-gated through a branch/PR workflow.
- `garden_index.py` — human-readable Novellas index builder.
- `singularity_weaver.py` — manual/read-only recovery/singularity artifact workflow helper.
- `splitter.py` — companion utility used by the singularity/recovery workflow.

Preserved non-executable data:

- `reflection-log.json` — December 2025 reflection artifact still referenced by a historical Reflection document. Presence here does not make it current status or authority.

Historical tool experiments are preserved under `docs/Archives/Legacy_Tools/`. Obsolete duplicate builders and broad HTML/root mutators are removed from the active workshop and remain recoverable through Git history.

Authority: `AUTHORITY.json`. Current generated state: `STATUS.json`. Automation does not confer authority or autonomy.
