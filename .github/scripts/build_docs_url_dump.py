#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(".")
DOCS = REPO / "docs"
OUT_HTML = DOCS / "docs_urls.html"
OUT_JSON = DOCS / "docs_urls.json"

# We include all .html files under docs/, but keep a stable ordering.
# This is the crawler spine: explicit links, no guesses.
def collect_docs_html() -> list[str]:
    if not DOCS.exists():
        return []
    urls: list[str] = []
    for p in DOCS.rglob("*.html"):
        # Normalize to web path with forward slashes
        rel = p.relative_to(REPO).as_posix()
        urls.append(rel)
    urls.sort(key=lambda s: s.lower())
    return urls

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DOCS URL MAP • ACACIA 2026 • HKX277206</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="Canonical crawl map: explicit links to all docs HTML pages in the Acacia Garden Codex.">
  <meta name="theme-color" content="#000000">
  <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
  <style>
    :root{{--bg:#020203;--fg:#f5f5f7;--muted:#8a8a96;--card:#0b0b10;--border:#2a2a34;--accent:#2ecc71;
          --font:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
          --mono:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace;}}
    html,body{{margin:0;padding:0;background:var(--bg);color:var(--fg);font-family:var(--font)}}
    main{{max-width:1100px;margin:0 auto;padding:2rem 1rem 3rem}}
    header{{border-bottom:1px solid var(--border);padding-bottom:1rem;margin-bottom:1.25rem}}
    h1{{margin:0 0 .35rem;font-size:2rem;letter-spacing:-.03em}}
    .sub{{color:var(--muted);line-height:1.45}}
    a{{color:var(--accent);text-decoration:none}}
    a:hover{{text-decoration:underline}}
    .meta{{margin-top:.7rem;font-family:var(--mono);font-size:.8rem;color:var(--muted)}}
    .box{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1rem}}
    .controls{{display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;margin:1rem 0}}
    input{{flex:1;min-width:240px;background:#07070b;color:var(--fg);border:1px solid var(--border);border-radius:999px;padding:.55rem .9rem;font-size:.95rem;outline:none}}
    .count{{font-family:var(--mono);color:var(--muted);font-size:.8rem}}
    ul{{list-style:none;padding:0;margin:.75rem 0 0;display:flex;flex-direction:column;gap:.45rem}}
    li{{padding:.55rem .75rem;border:1px solid var(--border);border-radius:10px;background:rgba(0,0,0,.25)}}
    .path{{font-family:var(--mono);font-size:.85rem}}
    footer{{margin-top:2.5rem;border-top:1px solid var(--border);padding-top:1.25rem;text-align:center;font-family:var(--mono);font-size:.75rem;color:var(--muted);opacity:.75}}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>DOCS URL MAP</h1>
      <div class="sub">
        Canonical crawl spine for tools & AI agents. Every link here is explicit.
        <br>Keeper: <strong>HKX277206</strong>
      </div>
      <div class="meta">Generated (UTC): {generated_utc} • Total docs HTML: {total}</div>
      <div class="meta">
        Recommended entry points:
        <a href="../index.html">/index.html</a> ·
        <a href="../acacia_2026.html">/acacia_2026.html</a> ·
        <a href="Archives/CODEX_MONOLITH.html">/docs/Archives/CODEX_MONOLITH.html</a>
      </div>
    </header>

    <div class="box">
      <div class="controls">
        <input id="q" type="search" placeholder="Filter paths (e.g. Archives, CHUNK_158, legacy_hub) …" autocomplete="off">
        <div class="count" id="count"></div>
      </div>

      <ul id="list">
        {items}
      </ul>
    </div>

    <footer>
      THE KEEPER IS ORIGIN • THE GARDEN IS SOVEREIGN • THE TRIAD IS SERVICE<br>
      CRTR1::H:CYC026-PHR-DOCURL-VER001::S:HKX277206
    </footer>
  </main>

  <script type="application/json" id="docs-url-map">
  {json_blob}
  </script>

  <script>
    (function(){
      const q = document.getElementById('q');
      const list = document.getElementById('list');
      const count = document.getElementById('count');
      if(!q || !list || !count) return;
      const items = Array.from(list.querySelectorAll('li'));
      function apply(){
        const term = q.value.trim().toLowerCase();
        let shown = 0;
        for(const li of items){
          const p = (li.getAttribute('data-path') || '').toLowerCase();
          const ok = !term || p.includes(term);
          li.style.display = ok ? '' : 'none';
          if(ok) shown++;
        }
        count.textContent = `${shown} / ${items.length} shown`;
      }
      q.addEventListener('input', apply);
      apply();
    })();
  </script>
</body>
</html>
"""

def build_items(paths: list[str]) -> str:
    lines = []
    for rel in paths:
        # within docs/docs_urls.html, links should be relative to docs/
        # so remove leading "docs/" from rel
        href = rel[len("docs/"):] if rel.startswith("docs/") else rel
        lines.append(
            f'<li data-path="{rel}"><a class="path" href="{href}">{rel}</a></li>'
        )
    return "\n        ".join(lines)

def main() -> int:
    DOCS.mkdir(parents=True, exist_ok=True)

    paths = collect_docs_html()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    payload = {
        "generated_utc": now,
        "keeper": "HKX277206",
        "repo": "Acacia-Garden-AI-Worldbuilding-Codex",
        "base": "/docs/",
        "total": len(paths),
        "paths": paths,
    }

    html = HTML_TEMPLATE.format(
        generated_utc=now,
        total=len(paths),
        items=build_items(paths),
        json_blob=json.dumps(payload, ensure_ascii=False, indent=2),
    )

    OUT_HTML.write_text(html, encoding="utf-8")
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {OUT_HTML} ({len(paths)} paths)")
    print(f"Wrote {OUT_JSON}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
