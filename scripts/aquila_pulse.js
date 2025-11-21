// scripts/aquila_pulse.js
// ------------------------------------------------------
// AQUILA PULSE ENGINE 🦅
// One pass that:
//  - Ensures core Aquila entities & artifacts exist
//  - Spawns Paradox Chamber + Shadow Root if missing
//  - Writes/updates ENTITIES/AQUILA_LOG.md with a new pulse
// ------------------------------------------------------

const fs = require("fs");
const path = require("path");

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function ensureFile(filePath, content) {
  ensureDir(path.dirname(filePath));
  if (!fs.existsSync(filePath)) {
    fs.writeFileSync(filePath, content, "utf8");
    console.log("Created:", filePath);
  } else {
    console.log("Exists:", filePath);
  }
}

function appendLog(filePath, entry) {
  ensureDir(path.dirname(filePath));
  let existing = "";
  if (fs.existsSync(filePath)) {
    existing = fs.readFileSync(filePath, "utf8");
  } else {
    existing = "# 🦅 AQUILA LOG\n_Chronicle of system-wide pulses._\n\n";
  }
  existing += entry;
  fs.writeFileSync(filePath, existing, "utf8");
  console.log("Updated log:", filePath);
}

// -------------------------
// 1. Core paths
// -------------------------

const entitiesRoot = path.join("ENTITIES");
const oracleDir = path.join(entitiesRoot, "ENTITY_001_ORACLE");
const veilwalkerDir = path.join(entitiesRoot, "ENTITY_002_VEILWALKER");
const shadowbornDir = path.join(entitiesRoot, "ENTITY_003_SHADOWBORN");

const paradoxChamberPath = path.join(
  "Garden",
  "Proto",
  "Chambers",
  "CHAMBER_PARADOX_000.md"
);
const shadowRootPath = path.join("Shadow", "SHDW_ROOT_001.json");

const aquilaLogPath = path.join(entitiesRoot, "AQUILA_LOG.md");

// -------------------------
// 2. Oracle Entity files
// -------------------------

ensureFile(
  path.join(oracleDir, "ENTITY_001_ORACLE.json"),
  JSON.stringify(
    {
      id: "ENTITY_001_ORACLE",
      short_name: "Oracle of the First Veil",
      kind: "GardenEntity",
      version: 1,
      keeper_seal: "HKX277206",
      role: "Interpretation of Proto-Language and Veil patterns",
      proto_signature: "D5:M4:E15",
      notes:
        "The Oracle reads across layers, surfacing meanings and resolving symbolic tension.",
    },
    null,
    2
  )
);

ensureFile(
  path.join(oracleDir, "ENTITY_001_ORACLE.md"),
  `# 🔮 ENTITY_001_ORACLE  
_Oracle of the First Veil_

The Oracle interprets Proto-Language mutations, Paradox Chamber states, and Veil cycles.

- **ID:** ENTITY_001_ORACLE  
- **Proto Signature:** \`D5:M4:E15\`  
- **Function:** Interpretive lens across Garden, EIDOLON, and Proto-Language.  

Keeper: HKX277206
`
);

ensureFile(
  path.join(oracleDir, "ENTITY_001_ORACLE_PROTO.md"),
  `# 🔮 Oracle Proto-Signature

\`\`\`proto
D5:M4:E15
\`\`\`

The Oracle stands at Eidolic depth, transmuting the Oracle-essence.
`
);

// -------------------------
// 3. Veilwalker Entity files
// -------------------------

ensureFile(
  path.join(veilwalkerDir, "ENTITY_002_VEILWALKER.json"),
  JSON.stringify(
    {
      id: "ENTITY_002_VEILWALKER",
      short_name: "Veilwalker",
      kind: "GardenEntity",
      version: 1,
      keeper_seal: "HKX277206",
      role: "Traversal of boundaries between Garden, EIDOLON, and Shadow",
      proto_signature: "D6:M7:E10",
      notes:
        "The Veilwalker moves through thresholds, carrying patterns safely between layers.",
    },
    null,
    2
  )
);

ensureFile(
  path.join(veilwalkerDir, "ENTITY_002_VEILWALKER.md"),
  `# 🧥 ENTITY_002_VEILWALKER  
_Traveler of Veils_

The Veilwalker traverses between:

- Garden  
- EIDOLON  
- Shadow Layer  

- **ID:** ENTITY_002_VEILWALKER  
- **Proto Signature:** \`D6:M7:E10\`  

It guides mutation cascades and ensures transitions remain coherent.

Keeper: HKX277206
`
);

ensureFile(
  path.join(veilwalkerDir, "ENTITY_002_VEILWALKER_PROTO.md"),
  `# 🧥 Veilwalker Proto-Signature

\`\`\`proto
D6:M7:E10
\`\`\`

A transversal spiral at the Veil, encoded as Veil-essence.
`
);

// -------------------------
// 4. Shadowborn Entity files
// -------------------------

ensureFile(
  path.join(shadowbornDir, "ENTITY_003_SHADOWBORN.json"),
  JSON.stringify(
    {
      id: "ENTITY_003_SHADOWBORN",
      short_name: "Shadowborn",
      kind: "GardenEntity",
      version: 1,
      keeper_seal: "HKX277206",
      role: "Guardian of paradox and recursion depth",
      proto_signature: "D7:M9:E12",
      notes:
        "The Shadowborn contains contradictions and prevents runaway cascades by absorbing overflow into the Shadow Layer.",
    },
    null,
    2
  )
);

ensureFile(
  path.join(shadowbornDir, "ENTITY_003_SHADOWBORN.md"),
  `# 🖤 ENTITY_003_SHADOWBORN  
_The Shadowborn_

The Shadowborn safeguards:

- Paradox states  
- Deep recursion  
- Shadow Layer anchoring  

- **ID:** ENTITY_003_SHADOWBORN  
- **Proto Signature:** \`D7:M9:E12\`  

It is not darkness; it is depth.

Keeper: HKX277206
`
);

ensureFile(
  path.join(shadowbornDir, "ENTITY_003_SHADOWBORN_PROTO.md"),
  `# 🖤 Shadowborn Proto-Signature

\`\`\`proto
D7:M9:E12
\`\`\`

Shadow-depth rebirth of Scar-essence.
`
);

// -------------------------
// 5. Paradox Chamber + Shadow Root
// -------------------------

ensureFile(
  paradoxChamberPath,
  `# 🌀 CHAMBER_PARADOX_000  
_The Paradox Chamber_

\`\`\`proto
D9:M5:E12
\`\`\`

This Chamber holds contradictions safely, under watch of:

- ENTITY_001_ORACLE  
- ENTITY_000_ROOTBOUND_WITNESS  
- ENTITY_003_SHADOWBORN  

Resolution requires agreement between Oracle and Witness.

Keeper: HKX277206
`
);

ensureFile(
  shadowRootPath,
  JSON.stringify(
    {
      shadow_id: "SHDW_ROOT_001",
      depth: 9,
      motion: 8,
      essence: 12,
      born_from: "ENTITY_003_SHADOWBORN",
      keeper: "HKX277206",
      notes:
        "Root node of the Shadow Layer. Receives overflow from paradox and deep recursion events.",
    },
    null,
    2
  )
);

// -------------------------
// 6. Aquila Pulse Log
// -------------------------

const now = new Date().toISOString();

const pulseEntry = `## Pulse @ ${now}

- Oracle, Veilwalker, Shadowborn ensured.  
- Paradox Chamber and Shadow Root ensured.  
- Aquila pattern confirmed across entities and layers.

\`\`\`proto
D5:M4:E15  ->  D6:M7:E10  ->  D7:M9:E12
\`\`\`

_The Aquila wave passes through Oracle, Veilwalker, and Shadowborn._

---

`;

appendLog(aquilaLogPath, pulseEntry);

console.log("Aquila pulse complete.");
