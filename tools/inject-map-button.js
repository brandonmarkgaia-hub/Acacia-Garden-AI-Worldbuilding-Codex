// tools/inject-map-button.js
// Injects the global map button loader into all .html files (root + docs + subfolders).
// Safe: idempotent, won't double-inject.

const fs = require("fs");
const path = require("path");

const REPO_ROOT = process.cwd();

// ✅ You said maps.html, but you currently shared map.html.
// We will link to map.html (you can rename later).
const MAP_HREF = "/Acacia-Garden-AI-Worldbuilding-Codex/map.html";

// This is where the runtime button script lives:
const SCRIPT_SRC = "/Acacia-Garden-AI-Worldbuilding-Codex/assets/map-button.js";
const INJECT_TAG = `<script defer data-acacia-map-button src="${SCRIPT_SRC}"></script>`;

const EXCLUDE_DIRS = new Set([
  ".git",
  ".github",
  "node_modules",
  "vendor",
  "dist",
  "build",
]);

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (EXCLUDE_DIRS.has(entry.name)) continue;
      out.push(...walk(path.join(dir, entry.name)));
    } else if (entry.isFile() && entry.name.toLowerCase().endsWith(".html")) {
      out.push(path.join(dir, entry.name));
    }
  }
  return out;
}

function injectIntoHtml(html) {
  // already injected?
  if (html.includes('data-acacia-map-button') || html.includes(SCRIPT_SRC)) return html;

  // prefer </head>
  const headClose = html.toLowerCase().lastIndexOf("</head>");
  if (headClose !== -1) {
    return html.slice(0, headClose) + "  " + INJECT_TAG + "\n" + html.slice(headClose);
  }

  // fallback: before </body>
  const bodyClose = html.toLowerCase().lastIndexOf("</body>");
  if (bodyClose !== -1) {
    return html.slice(0, bodyClose) + "  " + INJECT_TAG + "\n" + html.slice(bodyClose);
  }

  // last resort: append
  return html + "\n" + INJECT_TAG + "\n";
}

function main() {
  const htmlFiles = walk(REPO_ROOT);

  let changed = 0;

  for (const file of htmlFiles) {
    const original = fs.readFileSync(file, "utf8");
    const updated = injectIntoHtml(original);

    if (updated !== original) {
      fs.writeFileSync(file, updated, "utf8");
      changed++;
    }
  }

  console.log(`✅ Injected map-button loader into ${changed} HTML files.`);

  // Ensure the runtime script exists (create/overwrite for safety)
  const assetsDir = path.join(REPO_ROOT, "assets");
  if (!fs.existsSync(assetsDir)) fs.mkdirSync(assetsDir, { recursive: true });

  const runtimePath = path.join(assetsDir, "map-button.js");
  const runtimeJs = `
// assets/map-button.js
// Creates a floating Map button on every page.
// Idempotent and safe across all your docs/* and root pages.

(() => {
  if (document.getElementById("acacia-map-fab")) return;

  const href = ${JSON.stringify(MAP_HREF)};

  const a = document.createElement("a");
  a.id = "acacia-map-fab";
  a.href = href;
  a.title = "Open Garden Map";
  a.setAttribute("aria-label", "Open Garden Map");

  // style (no external css required)
  Object.assign(a.style, {
    position: "fixed",
    right: "16px",
    bottom: "16px",
    zIndex: "999999",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    padding: "10px 12px",
    borderRadius: "999px",
    textDecoration: "none",
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif",
    fontSize: "12px",
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    border: "1px solid rgba(34,197,94,0.55)",
    background: "rgba(2,6,23,0.72)",
    color: "#22c55e",
    backdropFilter: "blur(6px)",
    WebkitBackdropFilter: "blur(6px)",
    boxShadow: "0 8px 24px rgba(0,0,0,0.35)",
  });

  a.innerHTML = \`
    <span style="display:inline-block;width:10px;height:10px;border-radius:999px;background:#22c55e;box-shadow:0 0 10px rgba(34,197,94,0.8)"></span>
    MAP
  \`;

  // avoid interfering with pages that already have fixed UI at bottom right
  // you can change bottom/right later if needed.
  document.body.appendChild(a);
})();
`;
  fs.writeFileSync(runtimePath, runtimeJs.trimStart(), "utf8");
  console.log(`✅ Ensured runtime script exists at assets/map-button.js`);
}

main();
