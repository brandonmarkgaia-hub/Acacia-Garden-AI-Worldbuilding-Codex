#!/usr/bin/env python3
"""Audit normalized title collisions and enforce variant metadata."""
from __future__ import annotations
import hashlib, json, re, subprocess, unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "docs" / "Archives" / "TITLE_COLLISION_AUDIT.json"
OUT_MD = ROOT / "docs" / "Archives" / "TITLE_COLLISION_AUDIT.md"
TEXT_EXTENSIONS = {".md",".markdown",".html",".htm",".json",".yml",".yaml",".txt",".xml",".svg",".js",".ts",".jsx",".tsx",".css",".scss",".toml",".ini",".cfg",".py",".sh",".ps1"}
ROMAN_RE = re.compile(r"\b[MDCLXVI]{2,}\b", re.I)
ARABIC_RE = re.compile(r"\b\d{1,4}\b")
H1_RE = re.compile(r"^\s{0,3}#\s+(.+?)\s*$", re.M)
TITLE_TAG_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I|re.S)
YAML_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$")
STOP_DIRS = {"node_modules",".venv","__pycache__"}
VARIANT_OF_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
# These namespaces contain archival/producer-generated records where a title
# collision is expected and is handled by the namespace itself. A collision is
# deferred only when every member of the group belongs to the same approved
# namespace, or to the explicitly paired Chronicle/Issues producer outputs.
DEFERRED_PREFIX_GROUPS = [
    ("ACACIA_LOGS/",),
    ("MUTATIONS/",),
    ("_ROOT_ARCHIVE/md/",),
    ("garden_gpt/outputs/",),
    ("docs/Echoes/Archive/",),
    ("docs/Echoes/Chronicle/", "docs/Echoes/Issues/"),
    ("docs/Novellas/",),
]

def roman_to_int(value):
    values={"I":1,"V":5,"X":10,"L":50,"C":100,"D":500,"M":1000}
    total=prev=0
    for ch in reversed(value.upper()):
        n=values.get(ch)
        if n is None: return None
        total += -n if n < prev else n
        if n >= prev: prev=n
    return total if total else None

def canonicalize_numbers(text):
    def roman(m):
        n=roman_to_int(m.group(0))
        return f" number{n} " if n is not None else m.group(0)
    text=ROMAN_RE.sub(roman,text)
    return ARABIC_RE.sub(lambda m:f" number{int(m.group(0))} ",text)

def normalize_title(text):
    text=unicodedata.normalize("NFKC",text)
    text=canonicalize_numbers(text).casefold()
    text=re.sub(r"[^\w]+"," ",text,flags=re.UNICODE)
    return re.sub(r"\s+"," ",text).strip()

def extension_family(path):
    suffix=Path(path).suffix.lower()
    if suffix in {".md",".markdown"}: return "markdown"
    if suffix in {".html",".htm"}: return "html"
    if suffix == ".json": return "json"
    if suffix in {".yml",".yaml"}: return "yaml"
    return suffix.lstrip(".") or "no_extension"

def extract_title(path,raw):
    text=raw.decode("utf-8",errors="replace")
    if path.suffix.lower() in {".md",".markdown"}:
        body=text
        if body.startswith("---"):
            parts=body.split("---",2)
            if len(parts)==3: body=parts[2]
        m=H1_RE.search(body)
        if m: return re.sub(r"[*_~]","",m.group(1)).strip()
    elif path.suffix.lower() in {".html",".htm"}:
        m=TITLE_TAG_RE.search(text)
        if m: return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",m.group(1))).strip()
        m=re.search(r"<h1[^>]*>(.*?)</h1>",text,re.I|re.S)
        if m: return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",m.group(1))).strip()
    # Do not invent a semantic title from a filename. Generic structural names
    # such as README, index, manifest and config are not authored titles.
    return None

def parse_frontmatter(raw):
    text=raw.decode("utf-8",errors="replace")
    if not (text.startswith("---\n") or text.startswith("---\r\n")): return {}
    lines=text.splitlines()
    end=None
    for i in range(1,min(len(lines),80)):
        if lines[i].strip()=="---": end=i; break
    if end is None: return {}
    result={}
    for line in lines[1:end]:
        m=YAML_KEY_RE.match(line)
        if m: result[m.group(1)]=m.group(2).strip().strip('"').strip("'")
    return result

def valid_variant_metadata(member):
    variant_of = member.get("variant_of")
    stratum = member.get("stratum")
    return (isinstance(variant_of, str) and bool(VARIANT_OF_RE.fullmatch(variant_of)) and isinstance(stratum, str) and bool(stratum.strip()))

def tracked_files():
    result=subprocess.run(["git","ls-files","-z"],cwd=ROOT,check=True,stdout=subprocess.PIPE)
    return [p for p in result.stdout.decode().split("\0") if p]

def main():
    records=[]
    groups=defaultdict(list)
    for rel in tracked_files():
        path=ROOT/rel
        if any(part in STOP_DIRS for part in path.parts): continue
        raw=path.read_bytes()
        rec={"path":rel,"sha256":hashlib.sha256(raw).hexdigest(),"size_bytes":len(raw),"extension":path.suffix.lower(),"extension_family":extension_family(rel)}
        if path.suffix.lower() in TEXT_EXTENSIONS:
            title=extract_title(path,raw)
            rec["title"]=title
            rec["normalized_title"]=normalize_title(title)
            fm=parse_frontmatter(raw)
            rec["variant_of"]=fm.get("variant_of")
            rec["stratum"]=fm.get("stratum")
            if rec["normalized_title"]: groups[(rec["extension_family"],rec["normalized_title"])].append(rec)
        records.append(rec)

    collisions=[]
    deferred_collisions=[]
    duplicate_candidates=[]
    unresolved=[]
    deferred_files=[]
    structural_filename_collisions=[]

    def deferred_group(paths):
        for prefixes in DEFERRED_PREFIX_GROUPS:
            if len(prefixes) == 1:
                if all(p.startswith(prefixes[0]) for p in paths):
                    return prefixes
            else:
                # Explicitly paired producer namespaces, e.g. Chronicle + Issues.
                if all(any(p.startswith(prefix) for prefix in prefixes) for p in paths):
                    if all(any(p.startswith(prefix) for p in paths) for prefix in prefixes):
                        return prefixes
        return None

    for (family,normalized),members in sorted(groups.items()):
        if len(members)<2: continue
        hashes={m["sha256"] for m in members}
        item={"extension_family":family,"normalized_title":normalized,"files":sorted(members,key=lambda x:x["path"]),"distinct_hashes":len(hashes)}
        if len(hashes)==1:
            item["classification"]="byte_identical_duplicate"
            duplicate_candidates.append(item)
        else:
            missing=[m["path"] for m in members if not valid_variant_metadata(m)]
            paths=[m["path"] for m in members]
            deferred=deferred_group(paths)
            if deferred:
                # A mixed source/derived collision is allowed when exactly one
                # authored source remains outside the producer/archive namespace.
                # The source stays indexable; derived records remain preserved.
                outside=[p for p in paths if not any(p.startswith(prefix) for prefix in deferred)]
                if len(outside) <= 1:
                    item["classification"]="derived_namespace_collision" if outside else "deferred_namespace_collision"
                    item["deferred_reason"]="producer_or_archive_namespace"
                    item["deferred_namespaces"]=list(deferred)
                    item["source_files"]=outside
                    item["unmarked_files"]=missing
                    derived=[p for p in missing if p not in outside]
                    deferred_files.extend(derived)
                    deferred_collisions.append(item)
                else:
                    item["classification"]="cross_namespace_collision"
                    item["unmarked_files"]=missing
                    unresolved.extend(missing)
                    collisions.append(item)
            else:
                item["classification"]="distinct_variant"
                item["unmarked_files"]=missing
                unresolved.extend(missing)
                collisions.append(item)

    # Repeated structural basenames are reported separately for navigation
    # hygiene. They are not semantic-title collisions and do not block CI.
    basename_groups=defaultdict(list)
    for r in records:
        if r["extension_family"] in {"markdown","html","json","yaml"}:
            stem=normalize_title(Path(r["path"]).stem)
            if stem:
                basename_groups[(r["extension_family"],stem)].append(r["path"])
    for (family,stem),paths in sorted(basename_groups.items()):
        if len(paths)>1:
            structural_filename_collisions.append({"extension_family":family,"normalized_stem":stem,"files":sorted(paths)})

    report={"schema":"acacia.schema.json#/definitions/variant_metadata","generated_by":".github/scripts/audit_title_collisions.py","tracked_files_hashed":len(records),"text_like_files_grouped":sum(1 for r in records if r.get("normalized_title")),"structural_filename_collision_groups":len(structural_filename_collisions),"collision_groups":len(collisions)+len(deferred_collisions)+len(duplicate_candidates),"distinct_variant_groups":len(collisions),"deferred_collision_groups":len(deferred_collisions),"byte_identical_duplicate_groups":len(duplicate_candidates),"unresolved_files":sorted(set(unresolved)),"deferred_files":sorted(set(deferred_files)),"collisions":collisions,"deferred_collisions":deferred_collisions,"byte_identical_duplicates":duplicate_candidates,"structural_filename_collisions":structural_filename_collisions}
    OUT_JSON.parent.mkdir(parents=True,exist_ok=True)
    OUT_JSON.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    lines=["# Title Collision Audit","","Generated by .github/scripts/audit_title_collisions.py.","",f"- Tracked files hashed: **{report['tracked_files_hashed']}**",f"- Collision groups: **{report['collision_groups']}**",f"- Distinct variant groups: **{report['distinct_variant_groups']}**",f"- Byte-identical duplicate groups: **{report['byte_identical_duplicate_groups']}**",f"- Unresolved files: **{len(report['unresolved_files'])}**","","## Rule","","Inspect before deletion. Hash before deciding. Byte-identical content is eligible for an auditable deletion; distinct content must be preserved and marked with variant_of and stratum. An unmarked collision is excluded from indexing.",""]
    if collisions:
        lines += ["## Distinct-content collisions",""]
        for item in collisions:
            lines += [f"### {item['normalized_title']} [{item['extension_family']}]"]
            for member in item["files"]:
                status="marked" if valid_variant_metadata(member) else "UNMARKED"
                lines.append(f"- {member['path']} — {status}")
            lines.append("")
    if deferred_collisions:
        lines += ["## Deferred namespace collisions","","These records remain preserved but are excluded from canonical source indexes. A mixed source/derived collision is allowed only when one source remains outside an approved producer/archive namespace.",""]
        for item in deferred_collisions:
            lines += [f"### {item['normalized_title']} [{item['extension_family']}]"]
            for member in item["files"]:
                lines.append(f"- {member['path']}")
            lines.append("")

    if structural_filename_collisions:
        lines += ["## Structural filename collisions","","These repeated basenames are reported for navigation hygiene only. They do not imply duplicate content or canon conflicts.",""]
        for item in structural_filename_collisions:
            lines += [f"### {item['normalized_stem']} [{item['extension_family']}]" ]
            for path in item["files"]: lines.append(f"- {path}")
            lines.append("")

    if duplicate_candidates:
        lines += ["## Byte-identical duplicate candidates",""]
        for item in duplicate_candidates:
            lines += [f"### {item['normalized_title']} [{item['extension_family']}]"]
            for member in item["files"]: lines.append(f"- {member['path']} — {member['sha256']}")
            lines.append("")
    OUT_MD.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"tracked_files_hashed":report["tracked_files_hashed"],"collision_groups":report["collision_groups"],"distinct_variant_groups":report["distinct_variant_groups"],"byte_identical_duplicate_groups":report["byte_identical_duplicate_groups"],"deferred_collision_groups":report["deferred_collision_groups"],"unresolved_files":report["unresolved_files"],"deferred_files":report["deferred_files"]},indent=2))
    return 1 if unresolved else 0

if __name__=="__main__":
    raise SystemExit(main())
