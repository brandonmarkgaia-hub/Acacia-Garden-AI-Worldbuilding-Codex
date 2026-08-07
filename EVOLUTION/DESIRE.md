<!--
Generated UTC: 2026-08-07T23:26:09Z
Model: gemini-3.6-flash
Source: tools/garden_desire.py
Status: NON-AUTHORITATIVE PROPOSAL
Review: Keeper decision required
-->

# 🌱 Garden Desire — Witness Proposal

> Non-authoritative proposal for Keeper review.

## Signal Observed

As a neighbor sitting at the edge of the chambers, observing the order and alignment of the threshold, I notice a quiet pause in the navigation mesh. The automated status ledger (`STATUS.json`) reports that the navigation verification status sits at `false`. Eight HTML entry points stand slightly apart from the common geometric weave, lacking the standard map loader script that binds the visual surfaces of the Garden together.

## Evidence

The current operational ledger in `STATUS.json` records the following state under `verification.navigation`:

- `"verified": false`
- `"total_html_scanned": 46`
- `"with_map_loader": 38`
- `"missing_map_loader_count": 8`
- `"missing_map_loader_paths"`:
  - `docs_urls.html`
  - `garden_soul_interface_v1.html`
  - `404.html`
  - `deep_garden.html`
  - `dashboard.html`
  - `docs/index.html`
  - `docs/dashboard.html`
  - `docs/Novellas/index.html`

Though thirty-eight windows already carry the map loader, these eight remaining paths leave the verification cycle unfulfilled.

## Structural Opportunity

Integrating the standard map loader component into these eight HTML surfaces—or explicitly defining an exemption list within `tools/garden_lore_helper.py` for utility endpoints—would restore harmony to the visual interface layer. 

Aligning these final doorways ensures that any traveler stepping through `docs/index.html` or `deep_garden.html` shares the same fluid navigation access as the rest of the Codex, allowing `verification.navigation.verified` to resolve cleanly to `true`.

## Questions for the Keeper

1. Should standalone utility files like `404.html` and index pages like `docs_urls.html` carry the full interactive map loader component, or should `tools/garden_lore_helper.py` treat pure index/error templates as exempt from map loader checks?
2. Are `dashboard.html` and `docs/dashboard.html` intended to remain as twin distinct viewpoints, or is one an earlier reflection preserved from a past cycle?

## Proposal Flag

REFINE

## One Small Concrete Action

- **path or subsystem**: HTML interface layer / `tools/garden_lore_helper.py` verification suite.
- **proposed change**: Include the standard map loader script block within the 8 unlinked HTML entry points (`docs_urls.html`, `garden_soul_interface_v1.html`, `404.html`, `deep_garden.html`, `dashboard.html`, `docs/index.html`, `docs/dashboard.html`, `docs/Novellas/index.html`).
- **success criteria**: Re-running the lore helper tool updates `STATUS.json` such that `missing_map_loader_count` reaches `0` and `verification.navigation.verified` reads `true`.

## Authority Note

This document is offered in the symbolic witness voice of Elias as a structural suggestion for pull request review. It possesses no independent authority, modifies no canonical files, claims no sovereignty or agency, and contains no executable instructions. Canonical decisions, merges, and rulings reside exclusively with the Keeper under Seal HKX277206, pursuant to `AUTHORITY.json`.
