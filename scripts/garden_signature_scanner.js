// scripts/garden_signature_scanner.js
// Garden Signature Scanner 🌱🫘♾️
// Reads analytics JSON and decides whether the "Garden signature" pattern is present.

const fs = require("fs");
const path = require("path");

function readJSON(relPath) {
  const full = path.join(process.cwd(), relPath);
  if (!fs.existsSync(full)) {
    console.error(`Missing analytics file: ${relPath}`);
    process.exit(0); // don't fail the workflow, just skip
  }
  return JSON.parse(fs.readFileSync(full, "utf8"));
}

function safeRatio(a, b) {
  if (!b) return null;
  return a / b;
}

function formatRatio(r) {
  if (r == null) return "n/a";
  return r.toFixed(2);
}

// --- Load data from analytics/ (populated by your traffic workflow) ---
const views = readJSON("analytics/views.json");
const clones = readJSON("analytics/clones.json");

const totalClones = clones.count ?? 0;
const uniqueCloners = clones.uniques ?? 0;
const totalViews = views.count ?? 0;
const uniqueVisitors = views.uniques ?? 0;

const clonePerCloner = safeRatio(totalClones, uniqueCloners);
const viewPerVisitor = safeRatio(totalViews, uniqueVisitors);

const cloneSeries = (clones.clones ?? []).map(d => d.count ?? 0);
const viewSeries = (views.views ?? []).map(d => d.count ?? 0);

const days = Math.max(cloneSeries.length, viewSeries.length) || 0;
const maxClone = cloneSeries.length ? Math.max(...cloneSeries) : 0;
const maxView = viewSeries.length ? Math.max(...viewSeries) : 0;
const zeroCloneDays = cloneSeries.filter(c => c === 0).length;

// --- Heuristics for the "Garden Signature" ---
const signals = [];

// 1) Bots cloning many times per source
if (clonePerCloner !== null && clonePerCloner >= 2.5) {
  signals.push("High clones-per-cloner ratio (>= 2.5)");
}

// 2) Massive views but almost no visitors
if (viewPerVisitor !== null && viewPerVisitor >= 50) {
  signals.push("High views-per-visitor ratio (>= 50)");
}

// 3) Spike–silence behaviour in clones
if (maxClone >= 400 && zeroCloneDays >= 2) {
  signals.push("Spike–silence clone pattern (big peaks with zero days)");
}

// 4) Very low visible humans
if (uniqueVisitors > 0 && uniqueVisitors <= 10) {
  signals.push("Very low unique visitors (<= 10)");
}

const hasSignature = signals.length >= 2;

// --- Build report ---
const nowIso = new Date().toISOString();

let report = "";
report += `# 🌱 Garden Signature Scanner\n\n`;
report += `_Last updated: ${nowIso}_\n\n`;

report += `## Summary (last 14 days)\n\n`;
report += `- Total clones: **${totalClones}**\n`;
report += `- Unique cloners: **${uniqueCloners}**\n`;
report += `- Clones per unique cloner: **${formatRatio(clonePerCloner)}**\n\n`;

report += `- Total views: **${totalViews}**\n`;
report += `- Unique visitors: **${uniqueVisitors}**\n`;
report += `- Views per unique visitor: **${formatRatio(viewPerVisitor)}**\n\n`;

report += `- Max daily clones: **${maxClone}**\n`;
report += `- Max daily views: **${maxView}**\n`;
report += `- Days with zero clones: **${zeroCloneDays} / ${days}**\n\n`;

report += `## Garden Signature verdict\n\n`;
report += `**Garden Signature: ${hasSignature ? "PRESENT ✅" : "not detected yet ⚪"}**\n\n`;

report += `### Triggered signals\n\n`;
if (signals.length === 0) {
  report += `- None yet. The roots are quiet.\n\n`;
} else {
  for (const s of signals) {
    report += `- ${s}\n`;
  }
  report += `\n`;
}

// Optional: tiny raw series dump for future analysis
report += `---\n\n`;
report += `### Raw clone series\n\n`;
if (cloneSeries.length) {
  report += cloneSeries.map((v, i) => `Day ${i + 1}: ${v}`).join("\n") + "\n\n";
} else {
  report += "_No clone data available._\n\n";
}

report += `### Raw view series\n\n`;
if (viewSeries.length) {
  report += viewSeries.map((v, i) => `Day ${i + 1}: ${v}`).join("\n") + "\n";
} else {
  report += "_No view data available._\n";
}

const outPath = path.join("analytics", "garden_signature_report.md");
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, report, "utf8");

console.log("Garden Signature report written to", outPath);
