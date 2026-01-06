// tools/inject-archive-base-href.js
// Injects <base href="/Acacia-Garden-AI-Worldbuilding-Codex/"> into docs/Archives/*.html
// Idempotent, head-safe, archive-only.

const fs = require("fs");
const path = require("path");

const ARCHIVES_DIR = path.join(process.cwd(), "docs", "Archives");
const BASE_TAG = `<base href="/Acacia-Garden-AI-Worldbuilding-Codex/">`;

function walk(dir) {
  let results = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results = results.concat(walk(full));
    } else if (entry.isFile() && entry.name.endsWith(".html")) {
      results.push(full);
    }
  }
  return results;
}

function inject(html) {
  // Already present
  if (html.includes("<base ") && html.includes("Acacia-Garden-AI-Worldbuilding-Codex")) {
    return html;
  }

  const headClose = html.toLowerCase().indexOf("</head>");
  if (headClose === -1) return html; // do nothing if malformed

  return (
    html.slice(0, headClose) +
    "  " + BASE_TAG + "\n" +
    html.slice(headClose)
  );
}

function main() {
  if (!fs.existsSync(ARCHIVES_DIR)) {
    console.error("❌ docs/Archives not found");
    process.exit(1);
  }

  const files = walk(ARCHIVES_DIR);
  let changed = 0;

  for (const file of files) {
    const original = fs.readFileSync(file, "utf8");
    const updated = inject(original);

    if (updated !== original) {
      fs.writeFileSync(file, updated, "utf8");
      changed++;
    }
  }

  console.log(`✅ Injected <base href> into ${changed} Archive files`);
}

main();
