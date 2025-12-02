import { promises as fs } from "fs";
import path from "path";

const ROOT = process.cwd();
const ECHO_DIR = path.join(ROOT, "docs/Echoes");
const OUTPUT = path.join(ECHO_DIR, "echoes_index.json");

function autoTitle(name) {
  return name
    .replace(/_/g, " ")
    .replace(/\.md$/, "")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

async function scan(dir) {
  let out = [];
  const files = await fs.readdir(dir, { withFileTypes: true });

  for (const f of files) {
    const full = path.join(dir, f.name);
    if (f.isFile() && f.name.endsWith(".md")) {
      out.push({
        id: f.name.replace(/\.md$/, ""),
        title: autoTitle(f.name),
        file: f.name,
        path: full.replace(ROOT + "/", "")
      });
    }
    if (f.isDirectory()) {
      const deeper = await scan(full);
      out = out.concat(deeper);
    }
  }

  return out;
}

async function main() {
  const echoes = await scan(ECHO_DIR);

  const index = {
    version: "1.0.0",
    generated: new Date().toISOString(),
    total: echoes.length,
    echoes
  };

  await fs.writeFile(OUTPUT, JSON.stringify(index, null, 2));
  console.log("Updated:", OUTPUT);
}

main();
