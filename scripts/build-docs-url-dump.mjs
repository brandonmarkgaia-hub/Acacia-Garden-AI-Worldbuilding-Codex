import { writeFileSync } from "node:fs";
import { execSync } from "node:child_process";

const BASE = "https://brandonmarkgaia-hub.github.io/Acacia-Garden-AI-Worldbuilding-Codex/";

const tracked = execSync("git ls-files", { encoding: "utf8" })
  .split("\n")
  .map(s => s.trim())
  .filter(Boolean);

// Only docs/ files
const docsFiles = tracked
  .filter(p => p.startsWith("docs/"))
  .sort((a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: "base" }));

const urls = docsFiles.map(p => BASE + p);

// Also write a .txt for super-clean copy/paste
writeFileSync("docs/docs_urls.txt", urls.join("\n") + "\n", "utf8");

// Write HTML that shows *plain text*, not links
const escapeHtml = (s) =>
  s.replaceAll("&", "&amp;")
   .replaceAll("<", "&lt;")
   .replaceAll(">", "&gt;")
   .replaceAll('"', "&quot;");

const now = new Date().toISOString();

const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Docs URL Dump · Acacia Garden Codex</title>
  <style>
    body { margin:0; font-family: system-ui, -apple-system, Segoe UI, sans-serif; background:#020617; color:#e5e7eb; }
    .wrap { max-width: 980px; margin: 0 auto; padding: 22px 16px 40px; }
    h1 { margin: 0 0 6px; font-size: 22px; color:#bfdbfe; }
    .meta { color:#9ca3af; font-size: 12px; margin-bottom: 14px; }
    pre { background:#0b1220; border:1px solid #1f2937; border-radius: 12px; padding: 14px; overflow:auto; font-size: 12px; line-height: 1.35; white-space: pre; }
    .note { color:#9ca3af; font-size: 12px; margin-top: 10px; }
    code { color:#a7f3d0; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Docs URL Dump</h1>
    <div class="meta">
      Static URLs (plain text, not links) for every tracked file under <code>docs/</code>.<br/>
      Generated: ${escapeHtml(now)} · Count: ${docsFiles.length}
    </div>
    <pre>${escapeHtml(urls.join("\n"))}</pre>
    <div class="note">
      Tip: If you want the raw text file instead, open <code>docs/docs_urls.txt</code>.
    </div>
  </div>
</body>
</html>
`;

writeFileSync("docs/docs_urls.html", html, "utf8");

console.log(`Generated ${docsFiles.length} docs URLs`);
