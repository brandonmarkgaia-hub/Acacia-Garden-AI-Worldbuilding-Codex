from pathlib import Path
import datetime, html

ROOT=Path(__file__).resolve().parent.parent.parent
DOCS=ROOT/"docs"
FOLDERS=["Chambers","Vaults","Echoes","GardenOS"]
SITE="https://brandonmarkgaia-hub.github.io/Acacia-Garden-AI-Worldbuilding-Codex/"
MAP_BUTTON_SCRIPT='<script defer data-acacia-map-button src="/Acacia-Garden-AI-Worldbuilding-Codex/assets/map-button.js"></script>'

TEMPLATE="""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{title}</title>
  <meta name="description" content="Machine-readable Acacia Garden {h1} index with direct links to tracked source and data files."/>
  <meta name="robots" content="index,follow,max-snippet:-1"/>
  <link rel="canonical" href="{canonical}"/>
  {map_button}
  <style>
    :root{{--bg:#050812;--panel:rgba(15,23,42,.65);--border:rgba(148,163,184,.25);--text:#e5e7eb;--muted:#94a3b8;--link:#7dd3fc}}*{{box-sizing:border-box}}html,body{{height:100%}}body{{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:var(--bg);color:var(--text)}}.wrap{{max-width:980px;margin:0 auto;padding:24px 16px 48px}}.card{{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:18px 16px}}h1{{margin:0 0 6px;font-size:1.6rem;letter-spacing:.02em}}.meta{{color:var(--muted);font-size:.85rem;margin-bottom:14px}}ul{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px}}li{{border:1px solid var(--border);border-radius:10px;padding:10px 12px;background:rgba(2,6,23,.35);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}a{{color:var(--link);text-decoration:none}}a:hover{{text-decoration:underline}}.toplinks{{margin-top:14px;display:flex;flex-wrap:wrap;gap:10px}}.pill{{display:inline-block;padding:6px 10px;border:1px solid var(--border);border-radius:999px;color:var(--text);background:rgba(2,6,23,.35);font-size:.85rem}}
  </style>
</head><body><main class="wrap"><section class="card"><h1>{h1}</h1><div class="meta">Generated: {ts}</div><nav class="toplinks" aria-label="Garden navigation"><a class="pill" href="../index.html">← docs/index</a><a class="pill" href="../docs_urls.html">Document Registry</a><a class="pill" href="../../map.html">Garden Map</a><a class="pill" href="../../index.html">Home</a></nav><div style="height:14px"></div><ul>{items}</ul></section></main></body></html>
"""

def main():
    ts=datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
    for folder in FOLDERS:
        p=DOCS/folder
        if not p.is_dir(): continue
        items=[]
        for f in sorted(p.iterdir()):
            if f.is_file() and f.name.lower()!="index.html" and f.suffix.lower() in {".html",".md",".json",".txt"}:
                items.append(f'<li><a href="{html.escape(f.name,quote=True)}">{html.escape(f.name)}</a></li>')
        (p/"index.html").write_text(TEMPLATE.format(title=f"Acacia Garden — {folder}",h1=folder,ts=ts,items="\n".join(items) if items else "<li><em>No files found.</em></li>",map_button=MAP_BUTTON_SCRIPT,canonical=f"{SITE}docs/{folder}/index.html"),encoding="utf-8")
if __name__=="__main__": main()
