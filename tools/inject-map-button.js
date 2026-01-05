// node tools/inject-map-button.js
const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const TARGET_EXT = ".html";
const INJECT_TAG = `<script defer src="/Acacia-Garden-AI-Worldbuilding-Codex/docs/assets/global-map-button.js"></script>`;

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name);

    // Skip common junk
    if (entry.isDirectory()) {
      if (entry.name === ".git" || entry.name === "node_modules") continue;
      walk(p);
      continue;
    }

    if (!entry.isFile() || !p.endsWith(TARGET_EXT)) continue;

    const html = fs.readFileSync(p, "utf8");
    if (html.includes("global-map-button.js")) continue;

    // Inject before </body> if possible, else append
    let out = html;
    if (html.includes("</body>")) {
      out = html.replace("</body>", `  ${INJECT_TAG}\n</body>`);
    } else {
      out = html + "\n" + INJECT_TAG + "\n";
    }

    fs.writeFileSync(p, out, "utf8");
    console.log("Injected:", path.relative(ROOT, p));
  }
}

walk(ROOT);
console.log("Done.");
