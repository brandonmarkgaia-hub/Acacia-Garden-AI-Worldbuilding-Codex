from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent.parent
ARCH = ROOT / "docs" / "Archives"

BASE_TAG = '<base href="/Acacia-Garden-AI-Worldbuilding-Codex/">'

HEAD_RE = re.compile(r"(<head[^>]*>)", re.IGNORECASE)

def main():
    if not ARCH.exists():
        return

    for html_path in ARCH.glob("*.html"):
        txt = html_path.read_text(encoding="utf-8", errors="ignore")

        # If base already present, skip
        if "<base " in txt.lower():
            continue

        m = HEAD_RE.search(txt)
        if not m:
            continue

        insert_at = m.end()
        fixed = txt[:insert_at] + "\n  " + BASE_TAG + "\n" + txt[insert_at:]
        html_path.write_text(fixed, encoding="utf-8")

if __name__ == "__main__":
    main()
