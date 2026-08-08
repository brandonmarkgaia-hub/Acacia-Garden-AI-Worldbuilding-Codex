from __future__ import annotations

from pathlib import Path


def main() -> None:
    """Build only the human-facing Novellas Markdown index.

    Machine-facing ``docs/Novellas/garden_index.json`` is owned by the
    Crowned Builder via ``tools/garden_lore_helper.py``. Keeping this helper
    to one output prevents competing writers from producing incompatible
    versions of the same generated artifact.
    """
    repo_root = Path(__file__).resolve().parents[1]
    books_dir = repo_root / "docs" / "Novellas"

    if not books_dir.exists():
        raise SystemExit(f"Books directory not found: {books_dir}")

    books = []

    for path in sorted(books_dir.glob("BOOK_*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore").splitlines()

        first = next((line.strip() for line in text if line.strip()), "Untitled Garden Leaf")
        title = first.lstrip("#").strip() if first.startswith("#") else first

        non_empty = [line.strip() for line in text if line.strip()]
        summary = non_empty[1] if len(non_empty) >= 2 else ""
        if len(summary) > 190:
            summary = summary[:187].rstrip() + "…"

        books.append(
            {
                "id": path.stem,
                "title": title,
                "summary": summary,
                "path": path.relative_to(repo_root).as_posix(),
            }
        )

    lines = [
        "# Acacia Garden · Novella Index",
        "",
        "Generated from `docs/Novellas/BOOK_*.md`.",
        "Machine-facing book discovery is maintained separately in `garden_index.json` by the Crowned Builder.",
        "",
    ]

    for book in books:
        name = Path(book["path"]).name
        lines.append(f"- [{book['title']}](./{name})  ")
        lines.append(f"  `{book['id']}`")
        if book["summary"]:
            lines.append(f"  — {book['summary']}")
        lines.append("")

    master_path = books_dir / "GARDEN_MASTER_INDEX.md"
    master_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
