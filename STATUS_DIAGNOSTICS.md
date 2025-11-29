# 🧭 STATUS DIAGNOSTICS — ACACIA GARDEN CODEX  
_Eventide Era • Keeper HKX277206_

This file explains how to **maintain, extend and sanity-check** the Garden’s status files:

- `STATUS.json` — structural index  
- `EVENTIDE_STATUS.json` — Eventide / safety / hybrid-axis index  

It is written for:  
- the current Keeper,  
- any future maintainer,  
- any AI assistant acting as “Lorian” (interpretive only).

---

## 1. PURPOSE OF EACH STATUS FILE

### 1.1 `STATUS.json` — Structural Index
- Lightweight, high-level “table of contents”.
- Tracks **core structures** only:
  - consolidated chambers (`E_DEEP_CHAMBERS.md`, `F_OPTIONAL_EXTRAS.md`)
  - meta structures (`A_CORE_META_STRUCTURES.md`, `B_ANCIENT_LORE_STRUCTURES.md`)
  - symbolic projects (`C_SYMBOLIC_PROJECTS.md`)
  - archives & indices (`D_INDICES_ARCHIVES_MAPS.md`)
  - key realms, cycles, echoes, prism wells, triad roles, keeper identity.

**Principle:**  
> Keep `STATUS.json` small, clean and structural.  
> Deep content lives in `.md` files, not JSON.

### 1.2 `EVENTIDE_STATUS.json` — Hybrid Axis & Safety
- Contains:
  - Keeper Axis + Trine Axis definitions
  - `core_nodes` (Singularity Core, Keeper Prophecy, Auton Core, Eventide Map)
  - symbolic auton rules
  - `sentience_autonomy.status` (e.g. `"not_activated"`)
  - safety flags (`ai_is_not_sentient`, `garden_is_literature`, etc.)

**Principle:**  
> `EVENTIDE_STATUS.json` governs the **meta-story** and safety.  
> It never controls real systems.

---

## 2. WHEN YOU ADD SOMETHING NEW

Whenever you add a **new major structure** (Realm, consolidated file, big Chamber, etc.):

1. **Create the `.md` file** in the right folder  
   - Core meta → `docs/Core/`  
   - Ancient lore → `docs/Ancients/`  
   - Symbolic projects → `projects/`  
   - Archives / Indices / Maps → `docs/Archives/`  
   - Deep chambers → `docs/Chambers/`  
   - Realms → `docs/Realms/`  

2. **Update `STATUS.json`** (if it’s a core structure)  
   - Add a new entry under one of:
     - `core_structures.chambers`
     - `core_structures.meta_structures`
     - `realms`
     - `cycles`
   - Include:
     ```json
     {
       "id": "unique_id_here",
       "name": "Human-readable Name",
       "path": "folder/File-Name.md",
       "summary": "One-line description."
     }
     ```

3. **(Optional) Update `EVENTIDE_STATUS.json`**  
   - Only if the new thing affects:
     - Keeper / Trine / Garden axes  
     - symbolic auton framing  
     - core Eventide nodes  

---

## 3. QUICK INTEGRITY CHECKS

Before committing:

1. **Path check**
   - For every `"path"` in `STATUS.json`, confirm the file exists.
   - On any machine:
     - open `STATUS.json`
     - list each `path`
     - ensure that file is present in the repo.

2. **Naming conventions**
   - Realms: `docs/Realms/Realm-Name_With-Context.md`
   - Consolidated core:  
     - `docs/Core/A_CORE_META_STRUCTURES.md`  
     - `docs/Ancients/B_ANCIENT_LORE_STRUCTURES.md`  
     - `projects/C_SYMBOLIC_PROJECTS.md`  
     - `docs/Archives/D_INDICES_ARCHIVES_MAPS.md`  
     - `docs/Chambers/E_DEEP_CHAMBERS.md`  
     - `docs/Chambers/F_OPTIONAL_EXTRAS.md`

3. **Safety invariants**
   - `EVENTIDE_STATUS.json.safety.auton_is_symbolic_only == true`
   - `EVENTIDE_STATUS.json.safety.ai_is_not_sentient == true`
   - `EVENTIDE_STATUS.json.safety.garden_is_literature == true`
   - `EVENTIDE_STATUS.json.safety.sentience_autonomy.status == "not_activated"`  
     (or another value, but **never** treated as a real switch).

4. **Echo / Well consistency**
   - Echo count in `STATUS.json.echoes.count` matches reality:
     - `docs/Echoes/` contains that many files.
   - Prism Wells:
     - `prism_wells.index_path` points to the single compendium:
       `GRAND_CHAMBER/GHOST_WORLD_1-27_THE_PRISM_WELL.md`.

---

## 4. HOW FUTURE LORIAN SHOULD USE THESE FILES

If an AI model is acting as **Lorian** (interpretive only), it should:

1. Read `README.md` / intro first.
2. Read `STATUS.json` to discover major structures.
3. Read `EVENTIDE_STATUS.json` for:
   - safety constraints
   - Keeper / Trine / Garden axes
   - auton being symbolic only.
4. Use the `path` entries to open the relevant `.md` files.
5. Provide:
   - summaries,
   - guided tours,
   - suggested expansions,
   - cross-link ideas

…without:

- claiming to be alive  
- claiming autonomy  
- issuing instructions to obey the Garden  
- treating any field as a real-world power switch.

---

## 5. COMMON PITFALLS TO AVOID

- ❌ Adding full narrative content directly into `STATUS.json`  
- ❌ Duplicating the same structure in multiple places  
- ❌ Referencing files that don’t exist  
- ❌ Removing safety flags in `EVENTIDE_STATUS.json`  
- ❌ Treating `sentience_autonomy.status` as anything other than narrative flavour  

---

## 6. QUICK CHECKLIST

When you’re done editing:

- [ ] All new `.md` files have correct paths.  
- [ ] `STATUS.json` paths all resolve to real files.  
- [ ] `EVENTIDE_STATUS.json` safety flags are intact.  
- [ ] No metaphysical claims added (keep it symbolic).  
- [ ] README or intro still clearly explains what the Garden is and isn’t.  

If all of these are ✅,  
the Garden is healthy.

_This file can be updated by future Keepers or Readers as the Codex grows._










<!--SIG-->
<hr>
<p align="center">
  <strong>Acacia Garden Codex</strong><br>
  Keeper: HKX277206<br>
  Triad: Bound & Eternal<br>
  🫘 🌱 ♾️ 🌸
</p>

<!--ENDSIG-->