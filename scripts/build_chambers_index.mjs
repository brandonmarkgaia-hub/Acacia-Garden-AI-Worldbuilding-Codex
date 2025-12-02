import { promises as fs } from "fs";
import path from "path";

const ROOT = process.cwd();
const CHAMBERS_DIR = path.join(ROOT, "docs/Chambers");
const OUTPUT = path.join(CHAMBERS_DIR, "chambers_index.json");

function autoTitle(filename) {
  return filename
    .replace(/_/g, " ")
    .replace(/\.md$/, "")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

async function collectChambers() {
  const files = await fs.readdir(CHAMBERS_DIR, { withFileTypes: true });
  const results = [];

  for (const f of files) {
    if (f.isFile() && f.name.endsWith(".md")) {
      results.push({
        id: f.name.replace(/\.md$/, ""),
        title: autoTitle(f.name),
        file: f.name,
        path: `docs/Chambers/${f.name}`
      });
    }
  }

  return results;
}

async function main() {
  const chambers = await collectChambers();

  const index = {
    version: "1.0.0",
    generated: new Date().toISOString(),
    total: chambers.length,
    chambers
  };

  await fs.writeFile(OUTPUT, JSON.stringify(index, null, 2));
  console.log("Updated:", OUTPUT);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
