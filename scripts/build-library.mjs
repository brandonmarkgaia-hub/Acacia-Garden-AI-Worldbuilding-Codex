// scripts/build-library.mjs
import fs from "node:fs";
import path from "node:path";

const ROOT = process.cwd();
const LIB_DIR = path.join(ROOT, "docs", "Library");
const OUT_JSON = path.join(ROOT, "docs", "library_index.json");

function readText(p) {
  return fs.readFileSync(p, "utf8");
}

function pick(re, s) {
  const m = s.match(re);
  return m ? m[1].trim() : "";
}

function pickList(re, s) {
  const m = s.match(re);
  if (!m) return [];
  const raw = m[1].trim();
  // accept: ["a","b"] OR a, b OR a | b
  if (raw.startsWith("[") && raw.endsWith("]")) {
    try { return JSON.parse(raw); } catch { /* fallthrough */ }
  }
  return raw
    .split(/[,|]/g)
    .map(x => x.trim())
    .filter(Boolean);
}

function main() {
  if (!fs.existsSync(LIB_DIR)) {
    console.log(`[library] Missing ${LIB_DIR} (nothing to build)`);
    fs.writeFileSync(OUT_JSON, JSON.stringify({ ok:true, items:[] }, null, 2));
    return;
  }

  const files = fs.readdirSync(LIB_DIR).filter(f => f.toLowerCase().endsWith(".md"));
  const items = [];

  for (const f of files) {
    const full = path.join(LIB_DIR, f);
    const s = readText(full);

    const title  = pick(/^\s*title:\s*["']?(.+?)["']?\s*$/mi, s) || f.replace(/\.md$/i,"");
    const author = pick(/^\s*author:\s*["']?(.+?)["']?\s*$/mi, s);
    const year   = pick(/^\s*year:\s*["']?(.+?)["']?\s*$/mi, s);
    const tags   = pickList(/^\s*tags:\s*(.+?)\s*$/mi, s);

    const rel = path.posix.join("docs", "Library", f);

    items.push({
      id: f.replace(/\.md$/i,""),
      title,
      author,
      year,
      tags,
      url: rel
    });
  }

  items.sort((a,b)=> a.title.localeCompare(b.title));

  const payload = {
    ok: true,
    generated_utc: new Date().toISOString(),
    count: items.length,
    items
  };

  fs.writeFileSync(OUT_JSON, JSON.stringify(payload, null, 2));
  console.log(`[library] wrote ${OUT_JSON} (${items.length} items)`);
}

main();
