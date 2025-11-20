const fs = require("fs");
const path = require("path");

function expand(seedFile) {
  const seed = JSON.parse(fs.readFileSync(seedFile, "utf8"));
  const num = seed.number;
  const title = seed.title;
  const content = seed.body;

  const template = fs.readFileSync("garden/templates/bloom.md", "utf8")
    .replace(/{{num}}/g, num)
    .replace(/{{title}}/g, title)
    .replace(/{{body}}/g, content);

  const out = `Blooms/Bloom_${num}.md`;
  fs.writeFileSync(out, template);
  console.log("Generated:", out);
}

for (const file of fs.readdirSync("seedbox")) {
  if (file.endsWith(".json")) expand(path.join("seedbox", file));
}
