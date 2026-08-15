#!/usr/bin/env python3
"""Acacia Garden Gatekeeper — repository, HTML, links, and machine indexes."""
from __future__ import annotations
import json, re, sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parent.parent
SITE="brandonmarkgaia-hub.github.io"; PREFIX="/Acacia-Garden-AI-Worldbuilding-Codex/"
ARCHIVES=("docs/Archives/","_ROOT_ARCHIVE/"); SKIP={".git","node_modules","__pycache__",".venv","venv","_site"}
ATTR=re.compile(r'(?:href|src)\s*=\s*["\']([^"\']+)["\']',re.I)
DOCTYPE=re.compile(r'<!doctype\s+html\s*>',re.I); CHARSET=re.compile(r'<meta\b[^>]*charset\s*=\s*["\']?utf-8',re.I)
VIEWPORT=re.compile(r'<meta\b[^>]*name\s*=\s*["\']viewport["\']',re.I); DESC=re.compile(r'<meta\b[^>]*name\s*=\s*["\']description["\']',re.I)
CANON=re.compile(r'<link\b[^>]*rel\s*=\s*["\'][^"\']*canonical',re.I); NOINDEX=re.compile(r'<meta\b[^>]*name\s*=\s*["\']robots["\'][^>]*content\s*=\s*["\'][^"\']*noindex',re.I)
JSONLD=re.compile(r'<script\b[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>',re.I|re.S)
RETIRED=("CODEX_MONOLITH_CHUNK_","docs/Archives/CODEX_MONOLITH.html")

class P(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.tags=Counter(); self.ids=[]; self.lang=""; self.title=[]; self.in_title=False
    def handle_starttag(self,t,a):
        t=t.lower(); self.tags[t]+=1; d={k.lower():(v or "") for k,v in a}; self.ids += [d["id"]] if d.get("id") else []
        if t=="html": self.lang=d.get("lang","").strip()
        if t=="title": self.in_title=True
    def handle_startendtag(self,t,a): self.handle_starttag(t,a)
    def handle_endtag(self,t): self.in_title=False if t.lower()=="title" else self.in_title
    def handle_data(self,d): self.title.append(d) if self.in_title else None

def j(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
def htmls(): return [p for p in sorted(ROOT.rglob("*.html")) if p.is_file() and not any(x in SKIP for x in p.parts)]
def archive(rel): return rel.startswith(ARCHIVES)

def local(page,raw):
    raw=raw.strip()
    if not raw or raw.startswith(("#","//","data:","mailto:","tel:","javascript:")): return None
    u=urlsplit(raw)
    if u.scheme or u.netloc:
        if u.scheme not in {"http","https"} or u.netloc.lower()!=SITE or not u.path.startswith(PREFIX): return None
        s=unquote(u.path)
    else: s=unquote(u.path)
    if not s: return None
    if s.startswith(PREFIX): q=ROOT/s[len(PREFIX):]
    elif s.startswith("/"): return None
    else: q=page.parent/s
    q=q.resolve()
    try: q.relative_to(ROOT)
    except ValueError: return ROOT.parent/"__outside_project__"/"escape"
    return q/"index.html" if s.endswith("/") else q

def status_check():
    e=c=0; data=j("STATUS.json")
    for section in ("chambers","blooms","echoes","vaults","orchards"):
        vals=data.get(section,[])
        if not isinstance(vals,list): print(f"[ERROR] STATUS {section}: not a list"); e+=1; continue
        se=0
        for x in vals:
            raw=x if isinstance(x,str) else x.get("path") if isinstance(x,dict) else None; c+=1
            if not isinstance(raw,str) or not raw.strip() or not (ROOT/raw).exists(): print(f"[ERROR] STATUS {section}: missing path {raw!r}"); e+=1; se+=1
        print(f"[Gatekeeper] STATUS {section}: {len(vals)} checked, {se} errors")
    return e,c

def html_check():
    e=links=0; pages=htmls()
    for page in pages:
        rel=page.relative_to(ROOT).as_posix()
        try: text=page.read_text(encoding="utf-8")
        except Exception as x: print(f"[ERROR] HTML unreadable {rel}: {x}"); e+=1; continue
        p=P()
        try: p.feed(text); p.close()
        except Exception as x: print(f"[ERROR] HTML parse {rel}: {x}"); e+=1; continue
        req={"doctype":bool(DOCTYPE.search(text)),"html":p.tags["html"]==1,"lang":bool(p.lang),"head":p.tags["head"]==1,"body":p.tags["body"]==1,"title":p.tags["title"]==1 and bool("".join(p.title).strip()),"charset":bool(CHARSET.search(text)),"viewport":bool(VIEWPORT.search(text))}
        for k,ok in req.items():
            if not ok: print(f"[ERROR] HTML {rel}: missing/invalid {k}"); e+=1
        for ident,n in Counter(p.ids).items():
            if n>1: print(f"[ERROR] HTML {rel}: duplicate id {ident!r}"); e+=1
        for payload in JSONLD.findall(text):
            try: json.loads(payload)
            except Exception as x: print(f"[ERROR] HTML {rel}: invalid JSON-LD: {x}"); e+=1
        if archive(rel):
            if not (DESC.search(text) or NOINDEX.search(text)): print(f"[ERROR] HTML {rel}: archive requires description or noindex"); e+=1
        else:
            if not DESC.search(text): print(f"[ERROR] HTML {rel}: missing description"); e+=1
            if not CANON.search(text): print(f"[ERROR] HTML {rel}: missing canonical"); e+=1
        for raw in ATTR.findall(text):
            if not archive(rel) and any(x in unquote(urlsplit(raw).path) for x in RETIRED): print(f"[ERROR] HTML {rel}: active link to retired surface {raw}"); e+=1
            target=local(page,raw)
            if target is None: continue
            links+=1
            if target.is_dir() and (target/"index.html").exists(): continue
            if not target.exists(): print(f"[ERROR] HTML link {rel} -> {raw}"); e+=1
    print(f"[Gatekeeper] HTML: {len(pages)} pages; {links} local links/assets; {e} errors")
    return e,len(pages)+links

def exact_index(label,listed,actual,count=None):
    e=0; lc=Counter(listed); dup=[x for x,n in lc.items() if n>1]
    if dup: print(f"[ERROR] {label}: {len(dup)} duplicate paths"); e+=len(dup)
    ls=set(listed); ac=set(actual); miss=sorted(ac-ls); stale=sorted(ls-ac)
    if miss: print(f"[ERROR] {label}: {len(miss)} missing live paths (first: {miss[:3]})"); e+=len(miss)
    if stale: print(f"[ERROR] {label}: {len(stale)} stale paths (first: {stale[:3]})"); e+=len(stale)
    if count is not None and count!=len(listed): print(f"[ERROR] {label}: declared count {count} != entries {len(listed)}"); e+=1
    print(f"[Gatekeeper] {label}: {len(listed)} indexed / {len(actual)} live; {e} errors")
    return e,len(actual)

def machine_check():
    e=c=0
    jsons=("AUTHORITY.json","STATUS.json","machine-index.json","machine-discovery.json",".well-known/acacia.json","docs/Archives/GARDEN_MANIFEST.json","docs/Archives/FULL_CODEX_INDEX.json","docs/api/GARDEN_API_INDEX.json","docs/docs_urls.json","GARDEN_VERSION.json")
    texts=("README.md","DISCOVERY.md","llms.txt","llms-full.txt","AGENTS.md","robots.txt","sitemap.xml","CHECKSUMS.sha256")
    for rel in jsons:
        c+=1
        try: j(rel)
        except Exception as x: print(f"[ERROR] machine JSON {rel}: {x}"); e+=1
    for rel in texts:
        c+=1; p=ROOT/rel
        if not p.exists() or p.stat().st_size==0: print(f"[ERROR] machine missing/empty {rel}"); e+=1
    mi=j("machine-index.json"); entries=mi.get("entries",[]); listed=[x.get("path") for x in entries if isinstance(x,dict) and isinstance(x.get("path"),str)]
    actual=[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/"docs/Echoes").rglob("*.md"))]
    x,y=exact_index("machine-index",listed,actual,mi.get("counts",{}).get("total")); e+=x;c+=y
    du=j("docs/docs_urls.json"); listed=du.get("paths",du.get("files",du.get("entries",[])))
    if listed and isinstance(listed[0],dict): listed=[x.get("path") for x in listed if isinstance(x.get("path"),str)]
    suffix={".html",".md",".json",".txt"}; actual=[p.relative_to(ROOT/"docs").as_posix() for p in sorted((ROOT/"docs").rglob("*")) if p.is_file() and p.suffix.lower() in suffix]
    declared=du.get("count",du.get("counts",{}).get("total") if isinstance(du.get("counts"),dict) else None)
    x,y=exact_index("docs_urls",listed,actual,declared); e+=x;c+=y
    print(f"[Gatekeeper] Machine surfaces/indexes: {c} checked; {e} errors")
    return e,c

def main():
    print("[Gatekeeper] Full Director integrity audit")
    parts=(status_check(),html_check(),machine_check()); errors=sum(x for x,_ in parts); checked=sum(y for _,y in parts)
    print(f"[Gatekeeper] {'PASSED' if not errors else 'FAILED'}: {errors} error(s), {checked} checked items")
    return 0 if not errors else 1
if __name__=="__main__": sys.exit(main())
