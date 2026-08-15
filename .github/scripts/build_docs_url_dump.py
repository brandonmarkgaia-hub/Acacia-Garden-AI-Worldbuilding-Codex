#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[2]; DOCS_DIR=ROOT/"docs"; OUT_HTML=DOCS_DIR/"docs_urls.html"; OUT_JSON=DOCS_DIR/"docs_urls.json"
SITE="https://brandonmarkgaia-hub.github.io/Acacia-Garden-AI-Worldbuilding-Codex/docs/docs_urls.html"

def git_ls_files_docs():
    try: out=subprocess.check_output(["git","ls-files","docs"],cwd=ROOT,text=True)
    except Exception: return []
    vals=[]
    for line in out.splitlines():
        if not line.startswith("docs/"): continue
        rel=line[5:].strip()
        if rel and Path(rel).suffix.lower() in {".html",".md",".json",".txt"}: vals.append(rel)
    return sorted(vals)

HTML='''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Acacia Garden · Machine Document Registry</title>
  <meta name="description" content="Machine-readable and human-searchable registry of tracked Acacia Garden documents under docs/." />
  <meta name="robots" content="index,follow,max-snippet:-1" />
  <link rel="canonical" href="'''+SITE+'''" />
  <style>
    :root{--bg:#050812;--panel:rgba(15,23,42,.72);--border:rgba(148,163,184,.22);--text:#e5e7eb;--muted:#94a3b8;--link:#7dd3fc}*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg);color:var(--text)}.wrap{max-width:980px;margin:0 auto;padding:28px 16px 48px}.card{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:18px 16px}h1{margin:0 0 .35rem;font-size:1.8rem}p{margin:.35rem 0 1rem;color:var(--muted);line-height:1.55}a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}input{width:100%;padding:10px 12px;border-radius:10px;border:1px solid var(--border);background:rgba(2,6,23,.5);color:var(--text)}ul{list-style:none;padding:0;margin:14px 0 0}li{padding:8px 6px;border-bottom:1px solid rgba(148,163,184,.12)}.meta{font-size:.85rem;color:var(--muted)}
  </style>
</head><body><main class="wrap"><section class="card"><h1>Acacia Garden document registry</h1><p>Tracked machine-discoverable documents under <code>docs/</code>. Generated from Git, not hand-maintained.</p><p class="meta">Count: <strong id="count">0</strong></p><input id="q" aria-label="Filter document paths" placeholder="Filter paths…" autocomplete="off"/><ul id="list"></ul></section></main>
<script>const paths={PATHS};const q=document.getElementById('q'),list=document.getElementById('list'),count=document.getElementById('count');function base(){const p=location.pathname.split('/').filter(Boolean);return p.length?'/'+p[0]+'/':'/'}function href(p){return base()+'docs/'+p.split('/').map(encodeURIComponent).join('/')}function render(a){list.innerHTML='';count.textContent=String(a.length);for(const p of a){const li=document.createElement('li'),x=document.createElement('a');x.href=href(p);x.textContent=p;li.appendChild(x);list.appendChild(li)}}q.addEventListener('input',()=>{const t=q.value.toLowerCase().trim();render(t?paths.filter(p=>p.toLowerCase().includes(t)):paths)});render(paths);</script>
</body></html>'''

def main():
    DOCS_DIR.mkdir(parents=True,exist_ok=True); paths=git_ls_files_docs()
    payload={"generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),"scope":"tracked files under docs/ with extensions .html, .md, .json, and .txt","purpose":"Broad document-path registry for discovery. Its count is not expected to match machine-index.json.","count":len(paths),"paths":paths,"source":"git ls-files docs"}
    OUT_JSON.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    OUT_HTML.write_text(HTML.replace("{PATHS}",json.dumps(paths,ensure_ascii=False)),encoding="utf-8")
    print(f"Wrote {OUT_JSON} ({len(paths)} paths) and {OUT_HTML}"); return 0
if __name__=="__main__": raise SystemExit(main())
