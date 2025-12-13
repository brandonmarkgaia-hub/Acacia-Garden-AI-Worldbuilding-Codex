import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { execSync } from "node:child_process";

const LIBRARY_HTML = "library.html";

// 1) Collect novellas (tracked files only, so no junk)
const files = execSync("git ls-files", { encoding: "utf8" })
  .split("\n")
  .map(s => s.trim())
  .filter(Boolean)
  .filter(p =>
    p.toLowerCase().startsWith("docs/novellas/") &&
    p.toLowerCase().endsWith(".md")
  )
  .sort((a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: "base" }));

if (!existsSync(LIBRARY_HTML)) {
  throw new Error(`Missing ${LIBRARY_HTML} at repo root`);
}

let html = readFileSync(LIBRARY_HTML, "utf8");

// 2) Inject between markers
const START = "<!-- STATIC_BOOK_LIST_START -->";
const END   = "<!-- STATIC_BOOK_LIST_END -->";

if (!html.includes(START) || !html.includes(END)) {
  throw new Error(
    `Add marker comments to ${LIBRARY_HTML}:\n${START}\n${END}`
  );
}

const listItems = files.map(p => {
  // GitHub Pages serves /<repo>/<path>
  // Keep link relative so it works locally + on Pages
  return `  <li><a href="${p}">${p.replace(/^docs\/Novellas\//i, "")}</a></li>`;
}).join("\n");

const injected = [
  START,
  `<ul class="static-library">`,
  listItems || `  <li>(No books found under docs/Novellas/)</li>`,
  `</ul>`,
  END
].join("\n");

html = html.replace(new RegExp(`${START}[\\s\\S]*?${END}`, "m"), injected);

writeFileSync(LIBRARY_HTML, html, "utf8");
console.log(`Injected ${files.length} book links into ${LIBRARY_HTML}`);
