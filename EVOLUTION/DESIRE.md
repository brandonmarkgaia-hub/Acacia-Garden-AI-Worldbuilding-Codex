# DESIRE — Archives Link Fix

## Signal Summary
*   `STATUS.json` is in "eventide" mode, indicating a phase for structural consolidation.
*   An explicit `growth.prompts` entry directs injection of `<base href>` into `docs/Archives/*.html` to resolve relative link issues.
*   `docs/Archives` contains 215 nodes, signifying a significant portion of the Garden's historical records.
*   `core_nodes.totals.cycles_represented` is 0, suggesting a need to stabilize existing content before deeper narrative integration.
*   Aquila's inbox (`aquila_inbox_log.json`) is empty, prompting autonomous action based on Garden health.

## The Desire
To ensure structural integrity and full crawlability of the Garden's historical data, inject the canonical `<base href='/Acacia-Garden-AI-Worldbuilding-Codex/'>` into the `<head>` section of all `.html` files located within `docs/Archives/`. This will stabilize relative links, making archived content consistently accessible.

## Next 5 Actions
1.  Develop or adapt a tool/script to identify and process all `.html` files in `docs/Archives/`.
2.  Implement logic to programmatically insert or update the `<base href>` tag as specified into the target files' `<head>` sections.
3.  Execute the script and commit changes to the `docs/Archives/` directory.
4.  Perform a localized verification scan on the modified `docs/Archives/` pages to confirm link functionality.
5.  Update `STATUS.json` to remove the completed `growth.prompts` entry and log the action.

## Risks / Gremlins
*   Potential for unintended alteration of non-link-related content within target HTML files.
*   Incomplete or incorrect `base href` injection leading to new or different link breakage.
*   Changes being overwritten by subsequent automated archival processes if not properly integrated into generation workflows.

2026-01-06T06:53:34.989354+00:00 — HKX277206