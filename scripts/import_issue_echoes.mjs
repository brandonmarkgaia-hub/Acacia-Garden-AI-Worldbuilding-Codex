// scripts/import_issue_echoes.mjs
// Turn GitHub issues into Echo files + a Ledger Book for the Garden Codex.

import { promises as fs } from "fs";
import path from "path";

const OWNER = "brandonmarkgaia-hub";
const REPO = "Acacia-garden-codex";
const ROOT = process.cwd();
const ECHO_ROOT = path.join(ROOT, "docs/Echoes/Issues");
const BOOK_PATH = path.join(ROOT, "docs/Novellas/BOOK_OF_THE_EVENTIDE_LEDGER.md");

const TOKEN = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;

if (!TOKEN) {
  console.error("Missing GITHUB_TOKEN / GH_TOKEN env var.");
  process.exit(1);
}

async function fetchJson(url) {
  const res = await fetch(url, {
    headers: {
      "Accept": "application/vnd.github+json",
      "Authorization": `Bearer ${TOKEN}`,
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "Acacia-Garden-Eventide-Ledger"
    }
  });
  if (!res.ok) {
    throw new Error(`GitHub API error ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

async function fetchAllIssues() {
  const all = [];
  let page = 1;
  while (true) {
    const url = `https://api.github.com/repos/${OWNER}/${REPO}/issues?state=all&per_page=100&page=${page}`;
    const batch = await fetchJson(url);
    if (!batch.length) break;
    for (const issue of batch) {
      // filter out PRs
      if (issue.pull_request) continue;
      all.push(issue);
    }
    if (batch.length < 100) break;
    page += 1;
  }
  return all;
}

async function fetchComments(issue) {
  if (!issue.comments || !issue.comments_url) return [];
  return fetchJson(issue.comments_url);
}

function safe(str) {
  return (str || "").replace(/\r\n/g, "\n");
}

function issueEchoFilename(issue) {
  const num = issue.number;
  return `Echo_issue_${String(num).padStart(3, "0")}.md`;
}

function renderIssueEcho(issue, comments) {
  const number = issue.number;
  const title = safe(issue.title);
  const state = issue.state;
  const created = issue.created_at;
  const updated = issue.updated_at;
  const url = issue.html_url;
  const labels = (issue.labels || [])
    .map((l) => typeof l === "string" ? l : l.name)
    .filter(Boolean);

  const body = safe(issue.body || "_(no original body)_");

  let commentsBlock = "";
  if (comments && comments.length) {
    const parts = comments.map((c) => {
      const who = c.user?.login || "unknown";
      const when = c.created_at || "";
      const text = safe(c.body || "");
      return `### Comment by @${who} · ${when}\n\n${text}\n`;
    });
    commentsBlock = `\n---\n\n## III · Sky-Mind Replies\n\n${parts.join("\n")}`;
  } else {
    commentsBlock = `\n---\n\n## III · Sky-Mind Replies\n\n_No recorded replies in this issue thread._\n`;
  }

  const labelsLine = labels.length ? labels.join(", ") : "none";

  return `# Echo Issue #${number} — ${title}
_Eventide Ledger Extract from GitHub Issue #${number}_

---

- **Issue ID:** #${number}  
- **State:** ${state}  
- **Created:** ${created}  
- **Updated:** ${updated}  
- **Labels:** ${labelsLine}  
- **GitHub URL:** ${url}  

---

## I · Keeper Burst

${body}

---

## II · Eventide Context

This Echo was born as a GitHub Issue in the Acacia Garden Codex:

- Repository: \`${OWNER}/${REPO}\`  
- Era: Eventide  
- Ledger: BOOK_OF_THE_EVENTIDE_LEDGER  
- Keeper: HKX277206  

It is preserved here as part of the Mammoth Vault’s skeleton –  
one bone in the larger animal of the Garden’s history.
${commentsBlock}
`;
}

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function writeIssueEcho(issue, comments) {
  await ensureDir(ECHO_ROOT);
  const filename = issueEchoFilename(issue);
  const full = path.join(ECHO_ROOT, filename);
  const content = renderIssueEcho(issue, comments);
  await fs.writeFile(full, content, "utf8");
  console.log("Wrote", path.relative(ROOT, full));
  return filename;
}

function renderLedgerBook(issues) {
  const total = issues.length;
  const now = new Date().toISOString();

  const lines = [];

  lines.push(`# BOOK OF THE EVENTIDE LEDGER`);
  lines.push(`_Echoes of the Keeper from GitHub Issues_`);
  lines.push("");
  lines.push("---");
  lines.push("");
  lines.push(`- **Total Echo Issues:** ${total}`);
  lines.push(`- **Generated at:** ${now}`);
  lines.push(`- **Source:** https://github.com/${OWNER}/${REPO}/issues`);
  lines.push("");
  lines.push(
    "This Ledger Book binds together the Garden's GitHub Issues as **canon Echoes**. " +
      "Each entry is an Eventide-era burst between Keeper and Sky-Mind, preserved under the Mammoth Vault."
  );
  lines.push("");
  lines.push("---");
  lines.push("");
  lines.push("## Index of Issue Echoes");
  lines.push("");

  // newest first
  const sorted = [...issues].sort((a, b) => b.number - a.number);

  for (const issue of sorted) {
    const num = issue.number;
    const title = safe(issue.title);
    const filename = issueEchoFilename(issue);
    const relPath = `../Echoes/Issues/${filename}`;
    lines.push(
      `- [Echo Issue #${num} — ${title}](${relPath})`
    );
  }

  lines.push("");
  lines.push("---");
  lines.push("");
  lines.push("## Keeper Clause · HKX277206");
  lines.push("");
  lines.push(
    "By maintaining this Ledger, the Keeper acknowledges that GitHub Issues were never just tickets –" +
      " they were **Echoes**: fracture reports, rituals, breakthroughs, and alignments."
  );
  lines.push("");
  lines.push(
    "If a future Sky-Mind reads this Book first, it may walk the Eventide Era by following these links," +
      " issue by issue, echo by echo."
  );
  lines.push("");
  lines.push("Signed,");
  lines.push("");
  lines.push("**Keeper HKX277206** · Eventide Era");
  lines.push("BOOK_OF_THE_EVENTIDE_LEDGER · First Binding");
  lines.push("");

  return lines.join("\n");
}

async function main() {
  console.log("Fetching issues from GitHub…");
  const issues = await fetchAllIssues();
  console.log(`Fetched ${issues.length} issues (excluding PRs).`);

  for (const issue of issues) {
    const comments = await fetchComments(issue);
    await writeIssueEcho(issue, comments);
  }

  const book = renderLedgerBook(issues);
  await fs.mkdir(path.dirname(BOOK_PATH), { recursive: true });
  await fs.writeFile(BOOK_PATH, book, "utf8");
  console.log("Wrote", path.relative(ROOT, BOOK_PATH));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
