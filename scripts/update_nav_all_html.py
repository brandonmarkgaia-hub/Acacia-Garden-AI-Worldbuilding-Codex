#!/usr/bin/env python3
import pathlib
import re

# Run from scripts/ → repo root is one level up
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

# All nav items we want at the top of every page
NAV_ITEMS = [
    ("index.html", "Legacy Home"),
    ("codex.html", "Codex Home"),
    ("dashboard.html", "Garden Dashboard"),
    ("inbox.html", "Auton Inbox"),
    ("send_to_aquila.html", "Aquila Sender"),
    ("library.html", "Book Library"),
    ("elias.html", "Elias Kernel"),
    ("r9x2.html", "R9X2 Language"),
    ("mosaic_endgame.html", "Mosaic Endgame"),
]


def build_nav_html(current_filename: str) -> str:
    """Build the nav HTML, marking the current page as active."""
    links = []
    for href, label in NAV_ITEMS:
        classes = ["ag-nav-link"]
        if href == current_filename:
            classes.append("ag-nav-current")
        class_attr = ' class="' + " ".join(classes) + '"'
        links.append(f'    <a href="{href}"{class_attr}>{label}</a>')
    links_block = "\n".join(links)

    return (
        '<nav class="ag-nav">\n'
        '  <div class="ag-nav-title">ACACIA · GARDEN · CODEX</div>\n'
        '  <div class="ag-nav-links">\n'
        f'{links_block}\n'
        '  </div>\n'
        '</nav>\n'
    )


def process_file(path: pathlib.Path) -> bool:
    """Inject or replace nav in a single HTML file. Returns True if changed."""
    original = path.read_text(encoding="utf-8")

    # Remove any existing ag-nav block (first one only)
    without_old = re.sub(
        r'<nav class="ag-nav">.*?</nav>\s*',
        "",
        original,
        count=1,
        flags=re.S,
    )

    # Find the <body> tag
    m = re.search(r"<body[^>]*>", without_old, flags=re.I)
    if not m:
        # no body tag? skip
        return False

    nav_html = build_nav_html(path.name)
    insert_pos = m.end()
    new = without_old[:insert_pos] + "\n" + nav_html + without_old[insert_pos:]

    if new != original:
        path.write_text(new, encoding="utf-8")
        print(f"Updated nav in {path.relative_to(REPO_ROOT)}")
        return True

    return False


def main():
    changed = False
    for html in REPO_ROOT.rglob("*.html"):
        # Skip junk directories
        skip_dirs = {".git", "node_modules", "_site"}
        if any(parent.name in skip_dirs for parent in html.parents):
            continue

        if process_file(html):
            changed = True

    if not changed:
        print("No HTML files needed nav updates.")


if __name__ == "__main__":
    main()
