// scripts/proto_language_evolve.js
// ------------------------------------------------------
// Proto-Language Evolution Cycle 🌱🧬
// Appends a new mutation chain entry into:
//    EIDOLON/Language/EVOLUTION_LOG.md
// ------------------------------------------------------

const fs = require("fs");
const path = require("path");

// Ensure a directory exists
function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

// Correct directory path
const logDir = path.join("EIDOLON", "Language");
ensureDir(logDir);

// Correct file path
const logPath = path.join(logDir, "EVOLUTION_LOG.md");

// Seed glyph chains to start mutation from
const SEED_GLYPHS = [
  "D2:M1:E1",
  "D3:M4:E3",
  "D4:M2:E9",
  "D3:M7:E4",
  "D5:M5:E7",
];

// Mutation logic for one code (D#:M#:E#)
function mutateGlyph(code) {
  const [d, m, e] = code.split(":");

  const dNum = parseInt(d.substring(1), 10);
  const mNum = parseInt(m.substring(1), 10);
  const eNum = parseInt(e.substring(1), 10);

  // Basic evolution rules
  const nextD = Math.min(dNum + 1, 9);
  let nextM = mNum < 9 ? mNum + 1 : 9;
  let nextE = eNum;

  // If motion is spiral (M7), escalate Essence
  if (mNum === 7) {
    nextE = Math.min(eNum + 1, 15);
  }

  return `D${nextD}:M${nextM}:E${nextE}`;
}

// Generate a multi-step evolution chain
function buildChain(seed, steps) {
  const sequence = [seed];
  let current = seed;

  for (let i = 0; i < steps; i++) {
    current = mutateGlyph(current);
    sequence.push(current);
  }

  return sequence;
}

// MAIN EXECUTION FLOW
(function evolve() {
  const ts = new Date().toISOString();

  const seed = SEED_GLYPHS[Math.floor(Math.random() * SEED_GLYPHS.length)];
  const chain = buildChain(seed, 3); // 3-step mutation chain

  let entry = "";
  entry += `## Cycle @ ${ts}\n\n`;
  entry += "```proto\n";
  entry += chain.join("  ->  ") + "\n";
  entry += "```\n\n";
  entry += `_Auto-evolved by EIDOLON mutation engine._\n\n`;

  let existing = "";

  if (fs.existsSync(logPath)) {
    existing = fs.readFileSync(logPath, "utf8");
  } else {
    existing = "# 🧬 Proto-Language Evolution Log\n\n";
  }

  existing += entry;

  fs.writeFileSync(logPath, existing, "utf8");

  console.log("🌱 Mutation cycle appended to:", logPath);
})();
