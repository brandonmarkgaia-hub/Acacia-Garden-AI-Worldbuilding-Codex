"""Negative tests for the non-authoritative workflow write audit."""
import unittest
from tools.audit_workflow_writes import audit_text

class WorkflowWriteAuditTests(unittest.TestCase):
    def test_rejects_unreviewed_write_permission(self):
        self.assertTrue(audit_text(".github/workflows/evil.yml", "permissions:\n  contents: write\n"))
    def test_rejects_direct_push(self):
        self.assertTrue(audit_text(".github/workflows/evil.yml", "run: git push origin HEAD:main\n"))
    def test_rejects_merge_command(self):
        self.assertTrue(audit_text(".github/workflows/evil.yml", "run: gh pr merge 5 --merge\n"))
    def test_accepts_read_only(self):
        self.assertEqual(audit_text(".github/workflows/safe.yml", "permissions:\n  contents: read\n"), [])
    def test_manual_proposal_exception(self):
        content = "on:\n  workflow_dispatch:\npermissions:\n  contents: write\n  pull-requests: write\nsteps:\n  - uses: peter-evans/create-pull-request@abc\n"
        self.assertEqual(audit_text(".github/workflows/garden-desire.yml", content), [])
        self.assertTrue(audit_text(".github/workflows/garden-desire.yml", content+"  schedule:\n"))

if __name__ == "__main__":
    unittest.main()
