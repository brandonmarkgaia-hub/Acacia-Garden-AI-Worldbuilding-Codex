// scripts/generate_codex_indices.mjs
import { promises as fs } from "fs";
import path from "path";

const ROOT = process.cwd();

async function listMarkdownUnder(dir) {
  const results = [];
  async function walk(current) {
    let entries;
    try {
      entries = await fs.readdir(current, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) {
        await walk(full);
      } else if (
        entry.isFile() &&
        entry.name.toLowerCase().endsWith(".md")
      ) {
        const rel = path
          .relative(ROOT, full)
          .replace(/\\/g, "/");
        results.push(rel);
      }
    }
  }
  await walk(path.join(ROOT, dir));
  return results;
}

function sortByPath(a, b) {
  return a.path.localeCompare(b.path);
}

async function generateChambersIndex() {
  const canonDir = "docs/Chambers";
  const eidolonDir = "EIDOLON/Chambers";
  const protoDir = "Garden/Proto/Chambers";
  const ancientDir = "GRAND_CHAMBER/ANCIENT_CHAMBERS";

  const groups = [];

  // Canon + meta from docs/Chambers
  let canonFiles = [];
  try {
    canonFiles = await listMarkdownUnder(canonDir);
  } catch {
    canonFiles = [];
  }

  const canonEntries = [];
  const metaEntries = [];

  for (const rel of canonFiles) {
    const base = path.basename(rel);
    const entry = { path: rel };
    if (/^[EF]_/.test(base)) {
      metaEntries.push(entry);
    } else {
      canonEntries.push(entry);
    }
  }

  canonEntries.sort(sortByPath);
  metaEntries.sort(sortByPath);

  groups.push({
    id: "canon",
    label: "Canonical Chambers",
    entries: canonEntries,
  });

  groups.push({
    id: "meta",
    label: "Deep index & optional extras",
    entries: metaEntries,
  });

  // Eidolon
  let eidolonFiles = [];
  try {
    eidolonFiles = await listMarkdownUnder(eidolonDir);
  } catch {
    eidolonFiles = [];
  }
  eidolonFiles.sort();
  groups.push({
    id: "eidolon",
    label: "Eidolon / Potter Chambers",
    entries: eidolonFiles.map((p) => ({ path: p })),
  });

  // Proto
  let protoFiles = [];
  try {
    protoFiles = await listMarkdownUnder(protoDir);
  } catch {
    protoFiles = [];
  }
  protoFiles.sort();
  groups.push({
    id: "proto",
    label: "Proto Chambers",
    entries: protoFiles.map((p) => ({ path: p })),
  });

  // Ancient
  let ancientFiles = [];
  try {
    ancientFiles = await listMarkdownUnder(ancientDir);
  } catch {
    ancientFiles = [];
  }
  ancientFiles.sort();
  groups.push({
    id: "ancient",
    label: "Ancient Chambers",
    entries: ancientFiles.map((p) => ({ path: p })),
  });

  const index = {
    version: "1.0.0",
    generated_at: new Date().toISOString(),
    roots: {
      canon: canonDir,
      eidolon: eidolonDir,
      proto: protoDir,
      ancient: ancientDir,
    },
    groups,
  };

  const outPath = path.join(ROOT, "docs/Chambers/chambers_index.json");
  await fs.mkdir(path.dirname(outPath), { recursive: true });
  await fs.writeFile(
    outPath,
    JSON.stringify(index, null, 2),
    "utf8"
  );
  console.log("Wrote", outPath);
}

function labelFromEchoPath(rel) {
  const base = path.basename(rel).replace(/\.md$/i, "");
  if (/^Echo_\d+$/i.test(base)) {
    const num = base.match(/\d+/)?.[0] ?? "";
    return num ? `Echo ${num}` : base;
  }
  return base.replace(/_/g, " ");
}

function kindFromEchoPath(rel) {
  const base = path.basename(rel).replace(/\.md$/i, "");
  if (/^Echo_\d+$/i.test(base)) return "numbered";
  return "named";
}

async function generateEchoesIndex() {
  const echoDir = "docs/Echoes";
  let files = [];
  try {
    files = await listMarkdownUnder(echoDir);
  } catch {
    files = [];
  }

  const entries = files.map((p) => ({
    path: p,
    label: labelFromEchoPath(p),
    kind: kindFromEchoPath(p),
  }));

  // sort: numbered by number, then named alphabetically
  entries.sort((a, b) => {
    const aNum = a.kind === "numbered" ? parseInt(a.label.replace(/\D/g, ""), 10) : Infinity;
    const bNum = b.kind === "numbered" ? parseInt(b.label.replace(/\D/g, ""), 10) : Infinity;
    if (aNum !== bNum) return aNum - bNum;
    return a.label.localeCompare(b.label);
  });

  const index = {
    version: "1.0.0",
    generated_at: new Date().toISOString(),
    root: echoDir,
    total: entries.length,
    echoes: entries,
  };

  const outPath = path.join(ROOT, "docs/Echoes/echoes_index.json");
  await fs.mkdir(path.dirname(outPath), { recursive: true });
  await fs.writeFile(
    outPath,
    JSON.stringify(index, null, 2),
    "utf8"
  );
  console.log("Wrote", outPath);
}

async function main() {
  await generateChambersIndex();
  await generateEchoesIndex();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
