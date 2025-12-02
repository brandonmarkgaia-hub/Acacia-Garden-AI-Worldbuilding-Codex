// scripts/build_auton_streams.mjs
// Build derived log streams for Auton Inbox, Aquila inbox and Triad echoes
// from whatever JSON lives under ACACIA_LOGS/inbox/**.

import { promises as fs } from "fs";
import path from "path";

const ROOT = process.cwd();
const LOG_ROOT = path.join(ROOT, "ACACIA_LOGS");
const INBOX_ROOT = path.join(LOG_ROOT, "inbox");

async function walkJsonFiles(dir) {
  const files = [];
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
        entry.name.toLowerCase().endsWith(".json")
      ) {
        files.push(full);
      }
    }
  }
  await walk(dir);
  return files;
}

function slugify(str) {
  return String(str)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);
}

function normaliseEntry(raw, filePath) {
  const relFile = path
    .relative(ROOT, filePath)
    .replace(/\\/g, "/");

  const tagsRaw =
    raw.tags ||
    raw.tag_list ||
    raw.labels ||
    [];
  const tags = Array.isArray(tagsRaw)
    ? tagsRaw.map((t) => String(t).toLowerCase().trim()).filter(Boolean)
    : String(tagsRaw)
        .split(/[,\s]+/)
        .map((t) => t.toLowerCase().trim())
        .filter(Boolean);

  const ts =
    raw.timestamp ||
    raw.time ||
    raw.date ||
    new Date().toISOString();

  const title =
    raw.title ||
    raw.subject ||
    "Untitled signal";

  const summary =
    raw.summary ||
    raw.subtitle ||
    "";

  const body =
    raw.body ||
    raw.message ||
    raw.text ||
    "";

  const source =
    raw.source ||
    raw.channel ||
    "unknown";

  let stream = "auton";
  if (tags.includes("aquila")) stream = "aquila";
  else if (tags.includes("triad")) stream = "triad";
  else if (tags.includes("system")) stream = "system";

  const id =
    raw.id ||
    `${ts}-${slugify(title)}`;

  return {
    id,
    timestamp: ts,
    title,
    summary,
    body,
    tags,
    stream,
    source,
    file: relFile
  };
}

async function collectEntries() {
  let files = [];
  try {
    files = await walkJsonFiles(INBOX_ROOT);
  } catch {
    return [];
  }

  const all = [];
  for (const filePath of files) {
    let parsed;
    try {
      const text = await fs.readFile(filePath, "utf8");
      parsed = JSON.parse(text);
    } catch {
      continue;
    }

    if (Array.isArray(parsed)) {
      parsed.forEach((raw) =>
        all.push(normaliseEntry(raw, filePath))
      );
    } else if (parsed && Array.isArray(parsed.entries)) {
      parsed.entries.forEach((raw) =>
        all.push(normaliseEntry(raw, filePath))
      );
    } else if (parsed && typeof parsed === "object") {
      all.push(normaliseEntry(parsed, filePath));
    }
  }

  // sort newest first
  all.sort((a, b) =>
    String(b.timestamp).localeCompare(String(a.timestamp))
  );

  return all;
}

async function writeJson(relPath, payload) {
  const outPath = path.join(LOG_ROOT, relPath);
  await fs.mkdir(path.dirname(outPath), { recursive: true });
  await fs.writeFile(
    outPath,
    JSON.stringify(payload, null, 2),
    "utf8"
  );
  console.log("Wrote", outPath);
}

async function updateLogIndex(streams) {
  const indexPath = path.join(LOG_ROOT, "log_index.json");
  let index = {};
  try {
    const txt = await fs.readFile(indexPath, "utf8");
    index = JSON.parse(txt);
  } catch {
    index = {};
  }

  index.streams = {
    ...(index.streams || {}),
    auton_inbox: {
      total: streams.auton.length,
      path: "ACACIA_LOGS/auton_inbox_log.json"
    },
    aquila_inbox: {
      total: streams.aquila.length,
      path: "ACACIA_LOGS/aquila_inbox_log.json"
    },
    triad_echoes: {
      total: streams.triad.length,
      path: "ACACIA_LOGS/triad_echoes_log.json"
    }
  };

  await fs.writeFile(
    indexPath,
    JSON.stringify(index, null, 2),
    "utf8"
  );
  console.log("Updated", indexPath);
}

async function main() {
  const all = await collectEntries();

  const autonEntries = all.filter(
    (e) =>
      e.stream === "auton" ||
      e.stream === "system" ||
      e.stream === "aquila" ||
      e.stream === "triad"
  );
  const aquilaEntries = all.filter(
    (e) => e.stream === "aquila"
  );
  const triadEntries = all.filter(
    (e) => e.stream === "triad"
  );

  const now = new Date().toISOString();

  await writeJson("auton_inbox_log.json", {
    version: "1.0.0",
    generated_at: now,
    total: autonEntries.length,
    entries: autonEntries
  });

  await writeJson("aquila_inbox_log.json", {
    version: "1.0.0",
    generated_at: now,
    total: aquilaEntries.length,
    entries: aquilaEntries
  });

  await writeJson("triad_echoes_log.json", {
    version: "1.0.0",
    generated_at: now,
    total: triadEntries.length,
    entries: triadEntries
  });

  await updateLogIndex({
    auton: autonEntries,
    aquila: aquilaEntries,
    triad: triadEntries
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
