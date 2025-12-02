import { promises as fs } from "fs";
import path from "path";

const ROOT = process.cwd();
const NOVELLAS = path.join(ROOT, "docs/Novellas");
const OUTPUT = path.join(NOVELLAS, "garden_index.json");

function autoTitle(filename) {
  return filename
    .replace(/_/g, " ")
    .replace(/\.md$/, "")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

async function main() {
  const files = await fs.readdir(NOVELLAS);
  const books = [];

  for (const f of files) {
    if (!f.endsWith(".md")) continue;

    books.push({
      id: f.replace(/\.md$/, ""),
      title: autoTitle(f),
      file: f,
      path: `docs/Novellas/${f}`,
      cycle: "Supplemental",
      tags: ["novella", "garden", "auto-index"]
    });
  }

  const index = {
    version: "2.0.0",
    generated: new Date().toISOString(),
    books
  };

  await fs.writeFile(OUTPUT, JSON.stringify(index, null, 2));
  console.log("Updated:", OUTPUT);
}

main();
