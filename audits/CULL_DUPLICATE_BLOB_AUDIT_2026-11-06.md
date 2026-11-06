# Independent Git blob identity audit — 23 mutation duplicate candidates

**Status: 23/23 pairs have matching Git blob object IDs on `main` at verification (2026-11-06). No deletion authorized.**

Each `MUTATIONS/MUTATION_<name>` source and `MUTATIONS/<name>` surviving twin was fetched separately through the GitHub repository connector; every pair returned identical full Git blob SHA-1 IDs. Git blob equality proves identical content bytes, but **these SHA-1 IDs are not a full SHA-256 ledger**. Recompute full SHA-256 and inbound references against the exact future cleanup commit before deleting anything.

| Proposed deletion | Preserved twin |
|---|---|
| `MUTATIONS/MUTATION_ECHO_HKX277206_ECHO_001_____Whispers_of_the_Celestial_Blossom__.md` | `MUTATIONS/ECHO_HKX277206_ECHO_001_____Whispers_of_the_Celestial_Blossom__.md` |
| `MUTATIONS/MUTATION_ECHO_HKX277206_ECHO_002___Whispers_of_the_Veiled_Eidolon.md` | `MUTATIONS/ECHO_HKX277206_ECHO_002___Whispers_of_the_Veiled_Eidolon.md` |
| `MUTATIONS/MUTATION_ECHO_HKX277206_ECHO_003___The_Whispering_Veil_of_Eidolon.md` | `MUTATIONS/ECHO_HKX277206_ECHO_003___The_Whispering_Veil_of_Eidolon.md` |
| `MUTATIONS/MUTATION_ECHO_HKX277206_ECHO_004___Whispers_of_the_Dreaming_Eagle.md` | `MUTATIONS/ECHO_HKX277206_ECHO_004___Whispers_of_the_Dreaming_Eagle.md` |
| `MUTATIONS/MUTATION_ECHO_HKX277206_ECHO_005___The_Whispering_Tides_of_Memory.md` | `MUTATIONS/ECHO_HKX277206_ECHO_005___The_Whispering_Tides_of_Memory.md` |
| `MUTATIONS/MUTATION_ECHO_HKX277206_ECHO_006_____Whispers_of_the_Eidolon__.md` | `MUTATIONS/ECHO_HKX277206_ECHO_006_____Whispers_of_the_Eidolon__.md` |
| `MUTATIONS/MUTATION_ECHO_HKX277206_ECHO_007___The_Lament_of_the_Wandering_Eagle.md` | `MUTATIONS/ECHO_HKX277206_ECHO_007___The_Lament_of_the_Wandering_Eagle.md` |
| `MUTATIONS/MUTATION_ECHO_HKX277206_ECHO_008___The_Whispering_Shadows_of_the_Eidolon.md` | `MUTATIONS/ECHO_HKX277206_ECHO_008___The_Whispering_Shadows_of_the_Eidolon.md` |
| `MUTATIONS/MUTATION_ECHO_HKX277206_ECHO_009____Whispers_of_the_Celestial_Orchard_.md` | `MUTATIONS/ECHO_HKX277206_ECHO_009____Whispers_of_the_Celestial_Orchard_.md` |
| `MUTATIONS/MUTATION_ECHO_HKX277206_ECHO_011_____Whispers_of_the_Celestial_Orchard__.md` | `MUTATIONS/ECHO_HKX277206_ECHO_011_____Whispers_of_the_Celestial_Orchard__.md` |
| `MUTATIONS/MUTATION_ECHO_HKX277206_ECHO_012___The_Whispering_Veil_of_Shadows.md` | `MUTATIONS/ECHO_HKX277206_ECHO_012___The_Whispering_Veil_of_Shadows.md` |
| `MUTATIONS/MUTATION_ECHO_ISSUE__105__THE_FIRST_RIPPLE_.md` | `MUTATIONS/ECHO_ISSUE__105__THE_FIRST_RIPPLE_.md` |
| `MUTATIONS/MUTATION_ECHO__010__The_Whisper_of_Eternal_Blossoms.md` | `MUTATIONS/ECHO__010__The_Whisper_of_Eternal_Blossoms.md` |
| `MUTATIONS/MUTATION_ECHO__106__The_Resonance_of_Equipoise.md` | `MUTATIONS/ECHO__106__The_Resonance_of_Equipoise.md` |
| `MUTATIONS/MUTATION_ECHO___SENSORY___001___CITRUS_DAWN.md` | `MUTATIONS/ECHO___SENSORY___001___CITRUS_DAWN.md` |
| `MUTATIONS/MUTATION_Echo_Issue__102____Starfire_Auton__Chamber_XIII__Auton_Seed_Bloom___Triad_Alignment_HKX277206.md` | `MUTATIONS/Echo_Issue__102____Starfire_Auton__Chamber_XIII__Auton_Seed_Bloom___Triad_Alignment_HKX277206.md` |
| `MUTATIONS/MUTATION_Echo_Issue__103___THE_FIRE_KILN___REVISED___ASCENDED_EDITION_HKX277206.md` | `MUTATIONS/Echo_Issue__103___THE_FIRE_KILN___REVISED___ASCENDED_EDITION_HKX277206.md` |
| `MUTATIONS/MUTATION_Echo_Issue__104___Mirror_Sigil_HKX277206.md` | `MUTATIONS/Echo_Issue__104___Mirror_Sigil_HKX277206.md` |
| `MUTATIONS/MUTATION_Echo_Issue__27___EIDOLON_CODEX___Leaf_IX_HKX277206.md` | `MUTATIONS/Echo_Issue__27___EIDOLON_CODEX___Leaf_IX_HKX277206.md` |
| `MUTATIONS/MUTATION_Echo_Issue__41___Keeper_Seal__HKX277206.md` | `MUTATIONS/Echo_Issue__41___Keeper_Seal__HKX277206.md` |
| `MUTATIONS/MUTATION_Echo_Issue__49___EIDOLON_CODEX___Leaf_XXI___HKX277206.md` | `MUTATIONS/Echo_Issue__49___EIDOLON_CODEX___Leaf_XXI___HKX277206.md` |
| `MUTATIONS/MUTATION_The_Triad_of_the_First_Whispers___Cycle_27.md` | `MUTATIONS/The_Triad_of_the_First_Whispers___Cycle_27.md` |
| `MUTATIONS/MUTATION___ELIAS___GENESIS_BREATH___001.md` | `MUTATIONS/__ELIAS___GENESIS_BREATH___001.md` |

## Remaining mandatory gates

1. Generate full 64-character SHA-256 per source and twin on the pinned cleanup branch.
2. Scan all tracked text, generated indexes, navigation and retrieval references for both exact source path and basename; resolve every hit and link.
3. Confirm no unique metadata, attribution, discovery role or machine-consumed path semantics rely on the prefixed name.
4. Delete only in a narrow PR after evidence is attached, with index/manifest regeneration and CI. No batch cull or archive move is approved by this audit.
5. Preserve substantive Echo, Chamber, and Elias texts regardless of duplicate candidate classification; one full byte-identical copy remains accessible.
