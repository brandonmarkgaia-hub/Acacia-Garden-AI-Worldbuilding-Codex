const fs = require("fs");
const path = require("path");

const signature = fs.readFileSync("garden/signature.html", "utf8");

function walk(dir) {
  for (const file of fs.readdirSync(dir)) {
    const full = path.join(dir, file);

    if (fs.statSync(full).isDirectory()) walk(full);
    else if (full.endsWith(".md")) inject(full);
  }
}

function inject(file) {
  let content = fs.readFileSync(file, "utf8");
  content = content.replace(/<!--SIG-->[\s\S]*?<!--ENDSIG-->/g, "");
  content += `\n\n<!--SIG-->\n${signature}\n<!--ENDSIG-->`;
  fs.writeFileSync(file, content);
}

walk(".");
