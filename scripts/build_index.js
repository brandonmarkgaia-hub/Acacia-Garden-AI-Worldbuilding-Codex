const fs = require("fs");
const path = require("path");

const header = fs.readFileSync("garden/templates/index_header.md", "utf8");
const footer = fs.readFileSync("garden/templates/index_footer.md", "utf8");

function scan(dir) {
  const out = [];
  for (const file of fs.readdirSync(dir)) {
    const full = path.join(dir, file);
    if (file.endsWith(".md")) out.push(`- [${file.replace(".md","")}](${full})`);
  }
  return out.join("\n");
}

const sections = [
  { title: "Chambers", path: "Chambers" },
  { title: "Blooms", path: "Blooms" },
  { title: "Echoes", path: "Echoes" },
  { title: "Leaves", path: "Leaves" }
];

let md = header + "\n";

for (const { title, path: dir } of sections) {
  if (!fs.existsSync(dir)) continue;
  md += `\n## ${title}\n`;
  md += scan(dir);
  md += "\n";
}

md += footer;

fs.writeFileSync("index.md", md);
