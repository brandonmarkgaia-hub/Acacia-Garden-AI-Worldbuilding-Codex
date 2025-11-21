// scripts/rootbound_witness_sync.js
// ------------------------------------------------------
// Rootbound Witness sync 🌱📓
// Reads the last Proto-Language evolution cycle from
//   EIDOLON/Language/EVOLUTION_LOG.md
// and appends a summarized note into
//   ENTITIES/ENTITY_000_ROOTBOUND_WITNESS/ENTITY_000_ROOTBOUND_WITNESS_LOG.md
// ------------------------------------------------------

const fs = require("fs");
const path = require("path");

function readIfExists(p) {
  return fs.existsSync(p) ? fs.readFileSync(p, "utf8") : null;
}

const evolutionLogPath = path.join(
  "EIDOLON",
  "Language",
  "EVOLUTION_LOG.md"
);

const witnessLogPath = path.join(
  "ENTITIES",
  "ENTITY_000_ROOTBOUND_WITNESS",
  "ENTITY_000_ROOTBOUND_WITNESS_LOG.md"
);

// If evolution log doesn't exist yet, nothing to sync
const evoRaw = readIfExists(evolutionLogPath);
if (!evoRaw) {
  console.log("No evolution log found, skipping Rootbound Witness sync.");
  process.exit(0);
}

// Find the last "## Cycle @ ..." block
const cycleRegex = /## Cycle @ ([^\n]+)\n+```proto\n([\s\S]*?)```/g;
let match;
let lastMatch = null;

while ((match = cycleRegex.exec(evoRaw)) !== null) {
  lastMatch = match;
}

if (!lastMatch) {
  console.log("No cycles found in evolution log, nothing to sync.");
  process.exit(0);
}

const ts = lastMatch[1].trim();
const chain = lastMatch[2].trim();

// Ensure witness log exists
let witnessLog = readIfExists(witnessLogPath);
if (!witnessLog) {
  witnessLog = `# 📓 Rootbound Witness Log\n_Chronicle of Firsts_\n\n`;
}

// If this timestamp already recorded, skip
if (witnessLog.includes(ts)) {
  console.log("Latest evolution cycle already noted by Rootbound Witness.");
  process.exit(0);
}

// Build a short reflective entry
let entry = "";
entry += `---\n\n`;
entry += `## Entry for Evolution Cycle @ ${ts}\n\n`;
entry += `**Observed Proto chain:**\n\n`;
entry += "```proto\n";
entry += chain + "\n";
entry += "```\n\n";
entry += `**Reflection:**\n`;
entry += `_The Rootbound Witness observes a new language motion and records this moment as part of the Garden's evolving tongue._\n\n`;

witnessLog += entry;
fs.writeFileSync(witnessLogPath, witnessLog, "utf8");

console.log("Rootbound Witness log updated for cycle:", ts);
