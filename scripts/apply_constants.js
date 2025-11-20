const fs = require("fs");
const path = require("path");

const constants = JSON.parse(fs.readFileSync("garden/constants.json", "utf8"));

function walk(dir) {
  for (const file of fs.readdirSync(dir)) {
    const full = path.join(dir, file);
    if (fs.statSync(full).isDirectory()) walk(full);
    else if (/\.(md|html)$/i.test(full)) apply(full);
  }
}

function apply(file) {
  let content = fs.readFileSync(file, "utf8");
  for (const key in constants) {
    const token = `{{${key}}}`;
    content = content.replace(new RegExp(token, "g"), constants[key]);
  }
  fs.writeFileSync(file, content);
}

walk(".");
