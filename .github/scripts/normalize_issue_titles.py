import os
import re
import sys
import time
import requests

GH_TOKEN = os.environ.get("GH_TOKEN")
REPO = os.environ.get("GITHUB_REPOSITORY")

if not GH_TOKEN or not REPO:
    print("Missing GH_TOKEN or GITHUB_REPOSITORY in env.", file=sys.stderr)
    sys.exit(1)

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {GH_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
})

BASE_URL = f"https://api.github.com/repos/{REPO}"

ECHO_RE = re.compile(r"(ECHO:HKX277206[^\n]*)")
EIDOLON_RE = re.compile(r"(EIDOLON CODEX[^\n]*)", re.IGNORECASE)


def log(msg: str) -> None:
    print(msg, flush=True)


def fetch_issues():
    """Yield all issues (including closed), excluding PRs."""
    page = 1
    per_page = 100

    while True:
        params = {
            "state": "all",
            "per_page": per_page,
            "page": page,
        }
        resp = session.get(f"{BASE_URL}/issues", params=params)
        if resp.status_code != 200:
            log(f"Error fetching issues page {page}: {resp.status_code} {resp.text}")
            sys.exit(1)

        issues = resp.json()
        if not issues:
            break

        for issue in issues:
            # Skip PRs
            if "pull_request" in issue:
                continue
            yield issue

        page += 1
        # tiny throttle
        time.sleep(0.2)


def compute_new_title(issue) -> str | None:
    """Derive a normalized title from the issue body."""
    current_title = (issue.get("title") or "").strip()
    body = (issue.get("body") or "").strip()

    if not body:
        return None

    # 1) Prefer explicit ECHO line anywhere in the body
    m_echo = ECHO_RE.search(body)
    if m_echo:
        candidate = m_echo.group(1).strip()
    else:
        # 2) Prefer explicit EIDOLON CODEX line
        m_eidolon = EIDOLON_RE.search(body)
        if m_eidolon:
            candidate = m_eidolon.group(1).strip()
        else:
            # 3) Fallback: first non-empty line after "Message or Echo"
            lines = [ln.strip() for ln in body.splitlines()]
            # strip leading empties
            lines = [ln for ln in lines if ln]
            if not lines:
                return None

            # Skip a leading "### Message or Echo" heading if present
            if lines[0].lower().startswith("### message or echo"):
                lines = lines[1:]
                lines = [ln for ln in lines if ln]

            if not lines:
                return None

            candidate = re.sub(r"^#+\s*", "", lines[0]).strip()

    # Normalize whitespace
    candidate = " ".join(candidate.split())

    # If we ended up with something ultra-short, skip
    if len(candidate) < 5:
        return None

    # If current title is empty or clearly placeholder, we replace.
    # Otherwise, only change if the candidate is *different* but still "good".
    if not current_title or current_title.lower() in ("todo", "test", "fix", "echo"):
        pass  # always allow
    else:
        if candidate == current_title:
            return None

    return candidate


def update_issue_title(number: int, new_title: str):
    payload = {"title": new_title}
    resp = session.patch(f"{BASE_URL}/issues/{number}", json=payload)
    if resp.status_code not in (200, 201):
        log(f"❌ Failed to update issue #{number}: {resp.status_code} {resp.text}")
    else:
        log(f"✅ Updated issue #{number} → {new_title}")


def main():
    changed = 0
    skipped = 0

    for issue in fetch_issues():
        number = issue["number"]
        old_title = (issue.get("title") or "").strip()
        new_title = compute_new_title(issue)

        if not new_title:
            log(f"⏭ Skipping issue #{number} (no suitable derived title).")
            skipped += 1
            continue

        if new_title == old_title:
            log(f"⏭ Issue #{number} already has normalized title.")
            skipped += 1
            continue

        log(f"→ Issue #{number}: '{old_title}' → '{new_title}'")
        update_issue_title(number, new_title)
        changed += 1
        # small delay to respect rate limits
        time.sleep(0.2)

    log("")
    log(f"Done. Changed: {changed}, skipped: {skipped}")


if __name__ == "__main__":
    main()
