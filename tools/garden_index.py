from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    books_dir = repo_root / "docs" / "Novellas"

    if not books_dir.exists():
        raise SystemExit(f"Books directory not found: {books_dir}")

    books = []

    for path in sorted(books_dir.glob("BOOK_*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore").splitlines()

        # First non-empty line as title
        first = next((ln.strip() for ln in text if ln.strip()), "Untitled Garden Leaf")
        if first.startswith("#"):
            title = first.lstrip("#").strip()
        else:
            title = first

        # A tiny summary: second non-empty line if present
        rest_lines = [ln.strip() for ln in text if ln.strip()]
        summary = ""
        if len(rest_lines) >= 2:
            summary = rest_lines[1]
        if len(summary) > 190:
            summary = summary[:187].rstrip() + "…"

        rel_path = path.relative_to(repo_root).as_posix()

        books.append(
            {
                "id": path.stem,
                "title": title,
                "summary": summary,
                "path": rel_path,
            }
        )

    index = {"books": books}

    index_path = books_dir / "garden_index.json"
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Also write a human-facing master index markdown
    lines = [
        "# Acacia Garden · Novella Index",
        "",
        "Auto-generated from `docs/Novellas/BOOK_*.md`.",
        "This file is updated by GitHub Actions; you can edit the books themselves.",
        "",
    ]

    for b in books:
        name = Path(b["path"]).name
        lines.append(f"- [{b['title']}](./{name})  ")
        lines.append(f"  `{b['id']}`")
        if b.get("summary"):
            lines.append(f"  — {b['summary']}")
        lines.append("")

    master_path = books_dir / "GARDEN_MASTER_INDEX.md"
    master_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
