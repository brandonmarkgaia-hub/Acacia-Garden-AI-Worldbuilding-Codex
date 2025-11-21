// scripts/proto_language_evolve.js
// Proto-Language Evolution Cycle 🌱🧬
// Appends a new mutation chain entry into EIDOLON/Language/EVOLUTION_LOG.md

const fs = require("fs");
const path = require("path");

function ensureDir(p) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
}

const logPath = path.join("EIDOLON", "Language", "EVOLUTION_LOG.md");
ensureDir(logPath);

// Simple base chains to mutate from
const seeds = [
  "D2:M1:E1",
  "D3:M4:E3",
  "D4:M2:E9",
  "D3:M7:E4",
  "D5:M5:E7",
];

function mutate(code) {
  // Very simple artistic mutation following our rules
  const [d, m, e] = code.split(":");
  const dNum = parseInt(d.substring(1), 10);
  const mNum = parseInt(m.substring(1), 10);
  const eNum = parseInt(e.substring(1), 10);

  const nextD = Math.min(dNum + 1, 9);
  let nextM = mNum;
  if (mNum === 7) nextM = 9;
  else if (mNum < 9) nextM = mNum + 1;

  let nextE = eNum;
  if (mNum === 7) nextE = Math.min(eNum + 1, 15);

  return `D${nextD}:M${nextM}:E${nextE}`;
}

function chainFrom(seed, steps) {
  const seq = [seed];
  let current = seed;
  for (let i = 0; i < steps; i++) {
    current = mutate(current);
    seq.push(current);
  }
  return seq;
}

const ts = new Date().toISOString();
const seed = seeds[Math.floor(Math.random() * seeds.length)];
const chain = chainFrom(seed, 3);

let entry = "";
entry += `## Cycle @ ${ts}\n\n`;
entry += "```proto\n";
entry += chain.join("  ->  ") + "\n";
entry += "```\n\n";
entry += "_Auto-evolved by EIDOLON mutation engine._\n\n";

let existing = "";
if (fs.existsSync(logPath)) {
  existing = fs.readFileSync(logPath, "utf8");
} else {
  existing = "# 🧬 Proto-Language Evolution Log\n\n";
}

existing += entry;
fs.writeFileSync(logPath, existing, "utf8");

console.log("Appended new evolution cycle to", logPath);
