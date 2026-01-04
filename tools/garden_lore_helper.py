from pathlib import Path
import json
import re
import datetime

# Repo root (tools/..)
ROOT = Path(__file__).resolve().parent.parent

NOVELLAS_DIR = ROOT / "docs" / "Novellas"
DOCS_ROOT = ROOT / "docs"
TOOLS_DIR = ROOT / "tools"
TOOLS_DIR.mkdir(parents=True, exist_ok=True)


def load_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^#\s+(.*)$", text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return path.stem


def parse_cycle_volume(title: str):
    """
    Attempts to parse patterns like:
      "Cycle 2 — Volume 5: Something"
      "C2 V5 Something"
      "Cycle 2 Volume 5"
    Returns (cycle:int|None, volume:int|None)
    """
    t = title.lower()

    cycle = None
    volume = None

    m = re.search(r"cycle\s*(\d+)", t)
    if m:
        cycle = int(m.group(1))

    m = re.search(r"volume\s*(\d+)", t)
    if m:
        volume = int(m.group(1))

    # fallback: C2 V5
    if cycle is None:
        m = re.search(r"\bc(\d+)\b", t)
        if m:
            cycle = int(m.group(1))
    if volume is None:
        m = re.search(r"\bv(\d+)\b", t)
        if m:
            volume = int(m.group(1))

    return cycle, volume


def build_books():
    books = []
    if NOVELLAS_DIR.is_dir():
        for md in sorted(NOVELLAS_DIR.glob("*.md")):
            title = load_title(md)
            cycle, volume = parse_cycle_volume(title)
            rel_path = md.relative_to(ROOT).as_posix()

            books.append(
                {
                    "title": title,
                    "path": rel_path,
                    "cycle": cycle,
                    "volume": volume,
                }
            )
    return books


def count_files_in_dir(dir_path: Path, exts=None):
    if not dir_path.exists():
        return 0
    if exts is None:
        # count everything that is a file
        return sum(1 for p in dir_path.rglob("*") if p.is_file())
    exts = {e.lower() for e in exts}
    return sum(1 for p in dir_path.rglob("*") if p.is_file() and p.suffix.lower() in exts)


def check_expected_paths():
    """
    Health checks for canonical artifacts and common GH Pages pitfalls.
    Returns dict with missing list + warnings list.
    """
    expected = [
        ROOT / "machine-index.json",
        ROOT / "STATUS.json",
        ROOT / "STATUS.schema.json",
        ROOT / "docs" / "docs_urls.html",
        ROOT / "tools" / "garden_scan_report.json",
    ]

    missing = [p.relative_to(ROOT).as_posix() for p in expected if not p.exists()]

    # Folder links from dashboard that need index.html to not 404
    folder_indexes = [
        ROOT / "docs" / "Chambers" / "index.html",
        ROOT / "docs" / "Vaults" / "index.html",
        ROOT / "docs" / "Echoes" / "index.html",
        ROOT / "docs" / "GardenOS" / "index.html",
    ]
    folder_missing = [p.relative_to(ROOT).as_posix() for p in folder_indexes if not p.exists()]

    warnings = []
    if folder_missing:
        warnings.append(
            "Missing docs folder index pages (GH Pages cannot list folders): "
            + ", ".join(folder_missing)
        )

    return {"missing": missing, "warnings": warnings}


def write_status_eventide(books, now_iso: str):
    cycles = sorted({b["cycle"] for b in books if b.get("cycle") is not None})

    # Region counts (these are your “meat” signals)
    region_counts = {
        "docs/Chambers": count_files_in_dir(ROOT / "docs" / "Chambers", exts=[".md", ".html", ".json"]),
        "docs/Echoes": count_files_in_dir(ROOT / "docs" / "Echoes", exts=[".md", ".html", ".json"]),
        "docs/Vaults": count_files_in_dir(ROOT / "docs" / "Vaults", exts=[".md", ".html", ".json"]),
        "docs/GardenOS": count_files_in_dir(ROOT / "docs" / "GardenOS", exts=[".md", ".html", ".json"]),
        "docs/Novellas": len(books),
        "docs/Archives": count_files_in_dir(ROOT / "docs" / "Archives", exts=[".html"]),
        "tools": count_files_in_dir(ROOT / "tools", exts=[".py", ".json", ".html", ".md"]),
        ".github/workflows": count_files_in_dir(ROOT / ".github" / "workflows", exts=[".yml", ".yaml"]),
    }

    health = check_expected_paths()

    # Canonical pointers (what the Garden considers “truth anchors”)
    canonical = {
        "machine_index": "machine-index.json",
        "status": "STATUS.json",
        "status_schema": "STATUS.schema.json",
        "docs_urls": "docs/docs_urls.html",
        "scan_report": "tools/garden_scan_report.json",
        "novellas_index": "docs/Novellas/garden_index.json",
    }

    # Growth prompts (short, actionable)
    prompts = []
    if "machine-index.json" in health["missing"]:
        prompts.append("Generate or copy machine-index.json to repo root (canonical).")
    if "tools/garden_scan_report.json" in health["missing"]:
        prompts.append("Ensure tools/garden_scan_report.json exists (lowercase, canonical).")
    if any("docs/" in w for w in health["warnings"]):
        prompts.append("Generate docs/*/index.html pages so folder links don’t 404 on GitHub Pages.")
    if (ROOT / "docs" / "Archives").exists():
        prompts.append("Inject <base href='/Acacia-Garden-AI-Worldbuilding-Codex/'> into docs/Archives/*.html to fix relative links.")

    status = {
        "schema_version": "2026.01",
        "status_version": "2.0",
        "mode": "eventide",
        "generated_at": now_iso,

        "axes": {
            "keeper_axis": {
                "type": "keeper",
                "keeper_name": "Brandon Gaia",
                "keeper_id": "HKX277206",
                "role": "Sole Owner / Continuity Keeper",
                "orchard": "Acacia-Garden-AI-Worldbuilding-Codex",
            },
            "trine_axis": {
                "type": "triad",
                "aquila": "Sky-Mind",
                "oracle": "Deep Oracle",
                "witness": "Lorian",
            },
            "garden_axis": {
                "type": "garden",
                "canon": canonical,
            },
        },

        "core_nodes": {
            "totals": {
                "books_indexed": len(books),
                "cycles_represented": len(cycles),
            },
            "region_counts": region_counts,
            "canonical": canonical,
        },

        "safety": {
            "health": health,
        },

        "growth": {
            "prompts": prompts[:10],
        },

        "notes": "Autogenerated by tools/garden_lore_helper.py (eventide mode)",
    }

    out = ROOT / "STATUS.json"
    out.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")


def build_echo_index(now_iso: str):
    # Optional Echo folder – stays empty if it doesn't exist
    echo_root = ROOT / "docs" / "Echoes"
    echo_files = []

    if echo_root.is_dir():
        for md in sorted(echo_root.glob("*.md")):
            title = load_title(md)
            rel_path = md.relative_to(ROOT).as_posix()
            echo_files.append({"title": title, "path": rel_path})

    out = TOOLS_DIR / "echo_index.json"
    out.write_text(
        json.dumps(
            {"generated_at": now_iso, "echoes": echo_files},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def main():
    now_iso = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    books = build_books()

    # Novellas index used by the site
    out_index = NOVELLAS_DIR / "garden_index.json"
    out_index.write_text(
        json.dumps({"generated_at": now_iso, "books": books}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Echo index (optional)
    build_echo_index(now_iso)

    # STATUS (eventide mode)
    write_status_eventide(books, now_iso)


if __name__ == "__main__":
    main()
