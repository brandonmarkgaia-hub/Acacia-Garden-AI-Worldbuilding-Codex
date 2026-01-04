from pathlib import Path
import datetime
import html

ROOT = Path(__file__).resolve().parent.parent.parent  # .github/scripts -> repo root
DOCS = ROOT / "docs"

FOLDERS = ["Chambers", "Vaults", "Echoes", "GardenOS"]

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{title}</title>
  <style>
    body{{font-family:system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Arial; margin:24px;}}
    h1{{margin:0 0 8px 0;}}
    .meta{{opacity:.75; margin-bottom:18px;}}
    ul{{line-height:1.7}}
    a{{text-decoration:none}}
    a:hover{{text-decoration:underline}}
    .topnav{{margin: 0 0 18px 0;}}
  </style>
</head>
<body>
  <div class="topnav">
    <a href="../../index.html">Home</a> •
    <a href="../../library.html">Library</a> •
    <a href="../../dashboard.html">Dashboard</a> •
    <a href="../docs_urls.html">Docs URLs</a>
  </div>

  <h1>{h1}</h1>
  <div class="meta">Generated: {ts}</div>
  <ul>
    {items}
  </ul>
</body>
</html>
"""

def main():
    ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    for folder in FOLDERS:
        p = DOCS / folder
        if not p.exists():
            continue

        files = sorted([f for f in p.glob("*") if f.is_file() and f.name != "index.html"])
        items = []
        for f in files:
            name = html.escape(f.name)
            href = html.escape(f.name)
            items.append(f'<li><a href="{href}">{name}</a></li>')

        out = p / "index.html"
        out.write_text(
            TEMPLATE.format(
                title=f"Acacia Garden — {folder}",
                h1=f"{folder}",
                ts=ts,
                items="\n    ".join(items) if items else "<li><em>No files found.</em></li>",
            ),
            encoding="utf-8",
        )

if __name__ == "__main__":
    main()
