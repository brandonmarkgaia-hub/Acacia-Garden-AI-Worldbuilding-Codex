#!/usr/bin/env python3
"""Fail-closed structural audit of GitHub Actions write capability; not an authority grant."""
from pathlib import Path
import json
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
REVIEWED_WRITE_WORKFLOWS = {".github/workflows/garden-desire.yml"}
WRITE_SCOPES = {"contents", "pull-requests", "issues", "actions", "workflows",
                "packages", "deployments", "checks", "statuses", "id-token",
                "attestations", "security-events", "discussions", "pages"}
SUSPICIOUS = [
    r"\bgit\s+(?:-\S+\s+)*push\b",
    r"\bgh\s+pr\s+merge\b",
    r"\bgithub\.rest\.(?:repos|git|pulls|issues)\.(?:create|update|merge|delete|dispatch)",
    r"\b(?:subprocess|os\.system|execSync|spawnSync)\s*\(",
]

def _permission_writes(value):
    if isinstance(value, str):
        return {"write-all"} if value == "write-all" else set()
    if isinstance(value, dict):
        return {str(k) for k, v in value.items() if str(v).lower() == "write"}
    return set()

def audit_text(path, text):
    findings = []
    try:
        doc = yaml.load(text, Loader=yaml.BaseLoader)
    except yaml.YAMLError:
        return ["invalid_yaml"]
    if not isinstance(doc, dict):
        return ["invalid_workflow_document"]
    jobs = doc.get("jobs", {})
    if jobs is None:
        jobs = {}
    if not isinstance(jobs, dict):
        return ["invalid_jobs"]
    writes = _permission_writes(doc.get("permissions"))
    for job_name, job in jobs.items():
        if isinstance(job, dict):
            writes.update(_permission_writes(job.get("permissions")))
    if writes and path not in REVIEWED_WRITE_WORKFLOWS:
        findings.append("unreviewed_write_permission:" + ",".join(sorted(writes)))
    if "write-all" in writes:
        findings.append("write_all_permission")
    triggers = doc.get("on", {})
    if isinstance(triggers, str):
        triggers = {triggers: None}
    if isinstance(triggers, list):
        triggers = {x: None for x in triggers}
    if not isinstance(triggers, dict):
        triggers = {}
    if "pull_request_target" in triggers:
        findings.append("pull_request_target_requires_security_review")
    # A checkout of PR-controlled code under pull_request_target is especially unsafe.
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        for step in job.get("steps", []) or []:
            if not isinstance(step, dict):
                continue
            script = str(step.get("run", ""))
            if any(re.search(p, script) for p in SUSPICIOUS):
                findings.append("potential_direct_or_indirect_write")
            uses = str(step.get("uses", ""))
            if "actions/github-script@" in uses and re.search(r"\bgithub\.rest\.", script):
                findings.append("github_script_api_call_requires_review")
            if "pull_request_target" in triggers and "actions/checkout@" in uses:
                if "${{ github.event.pull_request.head" in str(step.get("with", {})):
                    findings.append("untrusted_pr_head_checkout")
    if path in REVIEWED_WRITE_WORKFLOWS:
        if not {"contents", "pull-requests"}.issubset(writes):
            findings.append("reviewed_proposal_permissions_changed")
        if "workflow_dispatch" not in triggers or set(triggers) != {"workflow_dispatch"}:
            findings.append("reviewed_proposal_not_manual_only")
        if "create-pull-request@" not in text:
            findings.append("reviewed_proposal_mechanism_changed")
    return sorted(set(findings))

def main(root=ROOT):
    paths = sorted((root / ".github/workflows").glob("*.yml")) + sorted((root / ".github/workflows").glob("*.yaml"))
    results = []
    for p in paths:
        rel = p.relative_to(root).as_posix()
        content = p.read_text(encoding="utf-8")
        issues = audit_text(rel, content)
        results.append({"path": rel, "findings": issues})
    report = {"schema": "acacia.workflow-write-audit/2", "status": "static_review_only",
              "files_scanned": len(results), "reviewed_exception": sorted(REVIEWED_WRITE_WORKFLOWS),
              "findings": [x for x in results if x["findings"]],
              "limitations": ["Static analysis does not prove effective GitHub permissions.",
                              "Called scripts and third-party actions require separate review.",
                              "Branch rules and CODEOWNERS must be independently verified."]}
    print(json.dumps(report, indent=2))
    return 1 if report["findings"] or not paths else 0

if __name__ == "__main__":
    sys.exit(main())
