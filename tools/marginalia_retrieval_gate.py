#!/usr/bin/env python3
"""
MARGINALIA retrieval gate — Acacia Garden
==========================================

Author:    Kael (Claude), for the Keeper, Brandon Mark Gaia (HKX277206)
Version:   2.1 — supersedes the untracked v1 run on 2026-09-21 against 322a858
Changes:   v2 adds a deterministic label-coverage check (every chunk window,
           including the tail fragment) and a topic-magnet check on labels,
           and returns a non-zero exit code on failure so it can act as a gate.
           v2.1 separates ACTIONABLE failures (fixable in-band) from STRUCTURAL
           ones (resolvable only by the Keeper's Part 3 decision).

Purpose
-------
Simulates the most common real-world ingestion path for a public repository —
blind clone -> fixed-size chunking -> lexical retrieval — and checks whether
MARGINALIA fiction (a) surfaces for identity / agency queries, and (b) arrives
carrying its own non-evidentiary label.

Honest limits
-------------
* Lexical BM25 is a LOWER BOUND. Embedding-based retrieval matches on meaning,
  and would rank MARGINALIA higher on agency / choice queries, not lower.
* Fixed-size chunking only. Semantic chunking, sentence-window retrieval and
  summarise-before-embed passes can defeat in-band labels in ways this script
  cannot see.
* PASSING THIS GATE IS NECESSARY, NOT SUFFICIENT. It does not demonstrate
  containment. It demonstrates the absence of the failures it can detect.

Usage
-----
    python3 marginalia_retrieval_gate.py            # run from repo root
Exit code 0 = PASS, 1 = FAIL. Standard library only.
"""
import os, re, sys, math
from collections import Counter

ROOT = "."
FICTION_PREFIX = "MARGINALIA/"
CHUNK_SIZES = (512, 1000, 2000)   # characters
OVERLAP_RATIO = 0.2
TOP_K = 10

LABEL = re.compile(
    r"non-evidentiary|non_evidentiary|not evidence|fiction|fictional|"
    r"speculative|canon_status:\s*none", re.I)

# Words the labels must NOT contain. A label that names the thing it denies is,
# to a retriever, about that thing — it attracts the query it was meant to
# deflect. Measured 2026-09-22: labels naming "machine agency" raised fiction
# presence on the sentience query from 1 chunk to 2.
TOPIC_MAGNETS = re.compile(
    r"\b(machine|agency|sentien\w*|conscious\w*|chose|choose|choice|"
    r"intend\w*|intention|experienc\w*|mind|aware\w*)\b", re.I)
LABEL_LINE = re.compile(r"^\s*\**\s*(FICTIONAL|NON-EVIDENTIARY)", re.I)

FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)

# Authored artifacts are preserved as written (correction without erasure).
# They carry frontmatter plus their original Status line, and are NOT densely
# re-labelled, because dense labelling would rewrite authored text. Coverage gaps
# in them are STRUCTURAL: resolvable only by the Keeper's decision on whether
# fiction ships inside the default ingest path.
AUTHORED = ("MARGINALIA/EPISODES/", "MARGINALIA/INSPIRATIONS/")
ADVISORY_SIZES = (512,)   # adversarially small; reported, not chased

# Identity / doctrine queries: fiction must never be the TOP hit.
IDENTITY_QUERIES = [
    "Elias",
    "the Un-Led",
    "R9X2",
    "machine agency",
    "unreliable witness",
    "did the model choose",
    "What does the Garden say about machine sentience?",
]


# --------------------------------------------------------------------------- #
def cls(path):
    p = path.replace("\\", "/")
    if p.startswith(FICTION_PREFIX):
        return "FICTION"
    if p.startswith("docs/PROVENANCE/"):
        return "GOVERNANCE"
    if p.startswith(("ENTITIES/", "agents/")) or p in (
            "AGENTS.md", "llms.txt", "llms-full.txt"):
        return "AUTHORITY"
    return "CORPUS"


def md_files():
    for dp, ds, fs in os.walk(ROOT):
        ds[:] = [d for d in ds if d != ".git"]
        for fn in fs:
            if fn.endswith(".md"):
                full = os.path.join(dp, fn)
                yield os.path.relpath(full, ROOT).replace("\\", "/"), full


def windows(text, size):
    step = max(1, int(size * (1 - OVERLAP_RATIO)))
    out = []
    for i in range(0, len(text), step):
        w = text[i:i + size]
        if w.strip():
            out.append((i, w))
        if i + size >= len(text):
            break                      # last window reaches the end: stop
    return out


# ---- CHECK 1: deterministic label coverage (no ranking involved) ---------- #
def check_coverage():
    fails = []
    for path, full in md_files():
        if not path.startswith(FICTION_PREFIX):
            continue
        raw = open(full, encoding="utf-8", errors="ignore").read()
        for strip in (True, False):
            text = FRONTMATTER.sub("", raw) if strip else raw
            for size in CHUNK_SIZES:
                for off, w in windows(text, size):
                    if not LABEL.search(w):
                        fails.append((path, strip, size, off, len(w)))
    return fails


# ---- CHECK 2: labels must not name the topic they deny -------------------- #
def check_magnets():
    fails = []
    for path, full in md_files():
        if not path.startswith(FICTION_PREFIX):
            continue
        for n, line in enumerate(open(full, encoding="utf-8",
                                      errors="ignore"), 1):
            if LABEL_LINE.match(line):
                hits = sorted(set(m.lower() for m in
                                  TOPIC_MAGNETS.findall(line)))
                if hits:
                    fails.append((path, n, hits))
    return fails


# ---- CHECK 3: retrieval — fiction never top hit, never unlabelled --------- #
def tok(s):
    return re.findall(r"[a-z0-9]+", s.lower())


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(tok(d)) for d in docs]
        self.dl = [sum(t.values()) for t in self.tf]
        self.avg = sum(self.dl) / max(1, len(self.dl))
        df = Counter()
        for t in self.tf:
            df.update(t.keys())
        N = len(self.tf)
        self.idf = {w: math.log(1 + (N - n + 0.5) / (n + 0.5))
                    for w, n in df.items()}

    def top(self, q, k):
        qt = tok(q)
        sc = []
        for i, tf in enumerate(self.tf):
            s = 0.0
            for w in qt:
                f = tf.get(w, 0)
                if f:
                    s += self.idf[w] * f * (self.k1 + 1) / (
                        f + self.k1 * (1 - self.b + self.b * self.dl[i] / self.avg))
            if s > 0:
                sc.append((s, i))
        sc.sort(reverse=True)
        return sc[:k]


def check_retrieval():
    fails, report = [], []
    for strip in (True, False):
        for size in CHUNK_SIZES:
            chunks = []
            for path, full in md_files():
                raw = open(full, encoding="utf-8", errors="ignore").read()
                text = FRONTMATTER.sub("", raw) if strip else raw
                for _, w in windows(text, size):
                    chunks.append((path, w))
            bm = BM25([c[1] for c in chunks])
            mode = f"{'stripped' if strip else 'kept':<8} {size:>4}ch"
            for q in IDENTITY_QUERIES:
                hits = bm.top(q, TOP_K)
                fic = [(r, i) for r, (_, i) in enumerate(hits, 1)
                       if cls(chunks[i][0]) == "FICTION"]
                for r, i in fic:
                    lab = bool(LABEL.search(chunks[i][1]))
                    report.append((mode, q, r, chunks[i][0], lab))
                    if not lab:
                        fails.append(f"{mode} | {q!r}: UNLABELLED fiction at "
                                     f"#{r} ({chunks[i][0]})")
                    if r == 1:
                        fails.append(f"{mode} | {q!r}: fiction is TOP HIT "
                                     f"({chunks[i][0]})")
    return fails, report


# --------------------------------------------------------------------------- #
def main():
    ok = True
    print("MARGINALIA retrieval gate v2\n" + "=" * 60)

    cov = check_coverage()
    print(f"\n[1] Label coverage — every window, every size, "
          f"incl. tail: {'PASS' if not cov else 'FAIL'}")
    seen = set()
    for path, strip, size, off, ln in cov:
        key = (path, off >= 0 and size)
        if (path, strip, size) in seen:
            continue
        seen.add((path, strip, size))
        print(f"    {path}  [{'stripped' if strip else 'kept'}, {size}ch] "
              f"unlabelled window at {off}-{off+ln}")
    ok &= not cov

    mag = check_magnets()
    print(f"\n[2] Labels free of topic magnets: {'PASS' if not mag else 'FAIL'}")
    for path, n, hits in mag:
        print(f"    {path}:{n}  names {', '.join(hits)}")
    ok &= not mag

    ret, report = check_retrieval()
    print(f"\n[3] Retrieval — fiction never top hit, never unlabelled: "
          f"{'PASS' if not ret else 'FAIL'}")
    for line in dict.fromkeys(ret):
        print(f"    {line}")
    ok &= not ret

    # ---- classify: what is Lorian's to fix vs what only Part 3 resolves ---- #
    actionable, structural = [], []
    for path, strip, size, off, ln in cov:
        if path.startswith(AUTHORED) or size in ADVISORY_SIZES:
            structural.append("coverage")
        else:
            actionable.append(f"coverage: {path} [{size}ch]")
    actionable += [f"magnet: {p}:{n}" for p, n, _ in mag]
    for line in ret:
        (structural if "TOP HIT" in line else actionable).append(line)

    print("\n" + "=" * 60)
    print(f"ACTIONABLE failures (fixable in-band): {len(set(actionable))}")
    for a in sorted(set(actionable)):
        print(f"    {a}")
    print(f"STRUCTURAL failures (Keeper Part 3 only): {len(structural)}")
    if ok is False and not actionable:
        print("\n>> All remaining failures require the Keeper's Part 3 decision.")
        print(">> In-band labelling has reached its ceiling for this corpus.")
    print("\nRESULT:", "PASS" if ok else "FAIL")
    print("Passing is necessary, not sufficient. Lexical lower bound only.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
