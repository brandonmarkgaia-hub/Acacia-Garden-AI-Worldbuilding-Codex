#!/usr/bin/env python3
"""Advisory audit of GitHub Actions write capabilities. No repository mutation."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
# This is an explicitly reviewed exception: manual workflow creates a PR, not canon.
REVIEWED_WRITE_WORKFLOWS = {".github/workflows/garden-desire.yml"}
WRITE_PERMISSION = re.compile(r"^\s*(contents|pull-requests|issues|actions|workflows|packages|deployments|checks|statuses):\s*write\s*(?:#.*)?$", re.M)
DIRECT_PUSH = re.compile(r"\bgit\s+(?:-\S+\s+)*push\b|\bgh\s+pr\s+merge\b")
CREDENTIAL = re.compile(r"secrets\.[A-Za-z_][A-Za-z0-9_]*(?:PAT|TOKEN)|GH_TOKEN|GITHUB_TOKEN")

def audit_text(path, text):
    findings = []
    writes = WRITE_PERMISSION.findall(text)
    if writes and path not in REVIEWED_WRITE_WORKFLOWS:
        findings.append("unreviewed_write_permission:" + ",".join(sorted(set(writes))))
    if DIRECT_PUSH.search(text):
        findings.append("direct_push_or_merge_command")
    if path in REVIEWED_WRITE_WORKFLOWS:
        if not {"contents", "pull-requests"}.issubset(set(writes)):
            findings.append("reviewed_proposal_permissions_changed")
        if "create-pull-request@" not in text or "workflow_dispatch:" not in text:
            findings.append("reviewed_proposal_mechanism_changed")
        if re.search(r"^\s*(push|schedule|pull_request|workflow_run):", text, re.M):
            findings.append("reviewed_proposal_not_manual_only")
    return findings

def main(root=ROOT):
    paths = sorted((root / ".github/workflows").glob("*.yml")) + sorted((root / ".github/workflows").glob("*.yaml"))
    results = []
    for p in paths:
        rel = p.relative_to(root).as_posix()
        content = p.read_text(encoding="utf-8")
        issues = audit_text(rel, content)
        results.append({"path": rel, "findings": issues, "credential_reference": bool(CREDENTIAL.search(content))})
    report = {"schema": "acacia.workflow-write-audit/1", "status": "static_review_only",
              "files_scanned": len(results), "reviewed_exception": sorted(REVIEWED_WRITE_WORKFLOWS),
              "findings": [x for x in results if x["findings"]],
              "limitations": ["Static patterns cannot prove effective GitHub token permissions.",
                              "GitHub branch protection and repository rules must be verified separately.",
                              "Indirect writes via invoked scripts and third-party actions need manual review.",
                              "Reviewed proposal workflow still requires PR review and branch protection."]}
    print(json.dumps(report, indent=2))
    return 1 if report["findings"] or not paths else 0

if __name__ == "__main__":
    sys.exit(main())
