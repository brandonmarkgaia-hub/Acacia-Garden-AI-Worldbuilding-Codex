from pathlib import Path
import datetime
import html

ROOT = Path(__file__).resolve().parent.parent.parent  # .github/scripts -> repo root
DOCS = ROOT / "docs"

# These are the folder index pages that get generated as docs/<Folder>/index.html
FOLDERS = ["Chambers", "Vaults", "Echoes", "GardenOS"]

# Canonical absolute loader so it works from ANY depth on GitHub Pages
MAP_BUTTON_SCRIPT = (
    '<script defer data-acacia-map-button '
    'src="/Acacia-Garden-AI-Worldbuilding-Codex/assets/map-button.js"></script>'
)

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{title}</title>

  {map_button}

  <style>
    :root {{
      --bg: #050812;
      --panel: rgba(15, 23, 42, 0.65);
      --border: rgba(148, 163, 184, 0.25);
      --text: #e5e7eb;
      --muted: #94a3b8;
      --link: #7dd3fc;
    }}
    html, body {{ height: 100%; }}
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
    }}
    .wrap {{
      max-width: 980px;
      margin: 0 auto;
      padding: 24px 16px 48px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 18px 16px;
    }}
    h1 {{
      margin: 0 0 6px;
      font-size: 1.6rem;
      letter-spacing: 0.02em;
    }}
    .meta {{
      color: var(--muted);
      font-size: 0.85rem;
      margin-bottom: 14px;
    }}
    ul {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 10px;
    }}
    li {{
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 12px;
      background: rgba(2, 6, 23, 0.35);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    a {{
      color: var(--link);
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    .toplinks {{
      margin-top: 14px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .pill {{
      display: inline-block;
      padding: 6px 10px;
      border: 1px solid var(--border);
      border-radius: 999px;
      color: var(--text);
      background: rgba(2, 6, 23, 0.35);
      font-size: 0.85rem;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>{h1}</h1>
      <div class="meta">Generated: {ts}</div>

      <div class="toplinks">
        <a class="pill" href="../index.html">← docs/index</a>
        <a class="pill" href="../docs_urls.html">docs_urls.html</a>
        <a class="pill" href="../../map.html">Garden Map</a>
        <a class="pill" href="../../index.html">Legacy Home</a>
      </div>

      <div style="height:14px"></div>

      <ul>
        {items}
      </ul>
    </div>
  </div>
</body>
</html>
"""


def main():
    ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    for folder in FOLDERS:
        p = DOCS / folder
        if not p.exists() or not p.is_dir():
            continue

        # List files (ignore index.html itself)
        items = []
        for f in sorted(p.iterdir()):
            if not f.is_file():
                continue
            if f.name.lower() == "index.html":
                continue

            # Only link typical content types; feel free to broaden later
            if f.suffix.lower() not in (".html", ".md", ".json", ".txt"):
                continue

            name = html.escape(f.name)
            href = html.escape(f.name)  # same folder, so direct
            items.append(f'<li><a href="{href}">{name}</a></li>')

        out = p / "index.html"
        out.write_text(
            TEMPLATE.format(
                title=f"Acacia Garden — {folder}",
                h1=f"{folder}",
                ts=ts,
                items="\n        ".join(items) if items else "<li><em>No files found.</em></li>",
                map_button=MAP_BUTTON_SCRIPT,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
