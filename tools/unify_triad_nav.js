#!/usr/bin/env node
/**
 * Unify navigation across ALL html files.
 * - Removes legacy hardcoded nav blocks (<nav class="ag-nav">...</nav>) including duplicates
 * - Removes ACACIA_NAV_INJECTED markers
 * - Injects ONE global nav script (triad_nav.js) into <head>
 */

const fs = require("fs");
const path = require("path");

const REPO_ROOT = process.cwd();
const ROOT_PREFIX = "/Acacia-Garden-AI-Worldbuilding-Codex/";

// Tweak exclusions if you want specific pages untouched
const EXCLUDE = new Set([
  // "nav_block.html",
]);

function walk(dir, out = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      // skip git + node stuff
      if (entry.name === ".git" || entry.name === "node_modules") continue;
      walk(full, out);
    } else {
      out.push(full);
    }
  }
  return out;
}

function stripLegacyNav(html) {
  let out = html;

  // Remove any ACACIA injected marker blocks (even if empty)
  out = out.replace(/<!--\s*ACACIA_NAV_INJECTED:START\s*-->[\s\S]*?<!--\s*ACACIA_NAV_INJECTED:END\s*-->\s*/g, "");

  // Remove ALL <nav class="ag-nav"> ... </nav> blocks (these cause double nav)
  out = out.replace(/<nav\s+class=["']ag-nav["'][\s\S]*?<\/nav>\s*/gi, "");

  // Also remove "ag-nav" variants like <nav class='ag-nav something'>
  out = out.replace(/<nav\s+class=["'][^"']*\bag-nav\b[^"']*["'][\s\S]*?<\/nav>\s*/gi, "");

  return out;
}

function ensureTriadScript(html, fileRelPath) {
  // If excluded file, do nothing
  const baseName = path.basename(fileRelPath);
  if (EXCLUDE.has(baseName)) return html;

  const scriptTag = `<script src="${ROOT_PREFIX}assets/triad_nav.js" defer></script>`;

  // Already present?
  if (html.includes("assets/triad_nav.js")) return html;

  // Inject before </head> if possible
  if (/<\/head>/i.test(html)) {
    return html.replace(/<\/head>/i, `  ${scriptTag}\n</head>`);
  }

  // If no head tag, inject at top
  return `${scriptTag}\n${html}`;
}

function main() {
  const files = walk(REPO_ROOT).filter(f => f.toLowerCase().endsWith(".html"));

  let changed = 0;

  for (const file of files) {
    const rel = path.relative(REPO_ROOT, file).replace(/\\/g, "/");
    const base = path.basename(rel);
    if (EXCLUDE.has(base)) continue;

    const before = fs.readFileSync(file, "utf8");
    let after = before;

    after = stripLegacyNav(after);
    after = ensureTriadScript(after, rel);

    if (after !== before) {
      fs.writeFileSync(file, after, "utf8");
      changed++;
      console.log(`✅ updated: ${rel}`);
    }
  }

  console.log(`\nDone. Files changed: ${changed}`);
}

main();
