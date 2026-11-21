"""Adversarial regression tests from the independent review of PR #261 (head 28e4f06).

Every test names the review finding it locks in (R = merge-blocking, C = coverage
for a protection the PR's own suite does not exercise, G = known gap).

ReviewKnownGaps began as expected failures at 28e4f06. PR #263 closed three of
them; the contradiction test remains an expected failure because textual
presence is not entailment.
"""
import hashlib
import os
import pathlib
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from validate import ROOT, validate

HERE = pathlib.Path(__file__).resolve().parent
VALIDATOR = HERE / "validate.py"
SOURCES = ("AUTHORITY.json", "AGENTS.md", "DISCOVERY.md", "STATUS.json", "llms.txt")
TOKEN = "OUTSIDE-ALLOWLIST-TOKEN-7731"


def record(**over):
    rec = {
        "id": "rev-001",
        "claim": "The Garden uses an AUTHORITY.json authority file.",
        "claim_type": "observed_text",
        "verification": "evidence_checked",
        "evidence": [{"path": "AUTHORITY.json", "excerpt": "\"schema\": \"acacia.authority/1.0\""}],
    }
    rec.update(over)
    return rec


def envelope(*records):
    return {"schema": "acacia.cev/0.1", "records": list(records)}


def run_cli(text):
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "records.json"
        path.write_text(text, encoding="utf-8")
        return subprocess.run([sys.executable, str(VALIDATOR), str(path)],
                              capture_output=True, text=True, timeout=60)


class ScratchRoot:
    """A throwaway evidence root holding copies of the allowlisted sources."""

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = pathlib.Path(self.tmp.name)
        self.root = base / "root"
        self.root.mkdir()
        for name in SOURCES:
            shutil.copyfile(ROOT / name, self.root / name)
        self.outside = base / "outside.txt"
        self.outside.write_text(TOKEN + "\n", encoding="utf-8")
        return self

    def __exit__(self, *exc):
        self.tmp.cleanup()


GOOD = ('{"id":"d-1","claim":"c","claim_type":"observed_text",%s'
        '"evidence":[{"path":"AUTHORITY.json","excerpt":"\\"schema\\""}]}')


class ReviewBlockingFindings(unittest.TestCase):
    """Fail at 28e4f06; pass once the merge-blocking corrections land."""

    def test_R1_duplicate_verification_key_rejected(self):
        # A first-key-wins reader sees independently_verified; validate.py saw the last key.
        text = '{"schema":"acacia.cev/0.1","records":[%s]}' % (
            GOOD % '"verification":"independently_verified","verification":"evidence_checked",')
        proc = run_cli(text)
        self.assertNotEqual(proc.returncode, 0, "duplicate keys must not validate")
        self.assertNotIn("Traceback", proc.stderr)

    def test_R1_duplicate_envelope_key_rejected(self):
        text = '{"schema":"bogus","schema":"acacia.cev/0.1","records":[%s]}' % (
            GOOD % '"verification":"evidence_checked",')
        self.assertNotEqual(run_cli(text).returncode, 0)

    def test_R1_nonstandard_json_constants_rejected(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                proc = run_cli('{"schema":"acacia.cev/0.1","records":[],"x":%s}' % token)
                self.assertEqual(proc.returncode, 2)

    def test_R2_lone_surrogate_excerpt_fails_closed(self):
        for excerpt in ("\ud800", "schema\udfff"):
            with self.subTest(excerpt=ascii(excerpt)):
                errors = validate(envelope(record(evidence=[{"path": "AUTHORITY.json", "excerpt": excerpt}])))
                self.assertTrue(any("excerpt absent" in e for e in errors))

    def test_R2_non_list_records_reported_without_traceback(self):
        for value in ("null", "5", "true", "3.5"):
            with self.subTest(records=value):
                proc = run_cli('{"schema":"acacia.cev/0.1","records":%s}' % value)
                self.assertEqual(proc.returncode, 1)
                self.assertIn("Invalid CEV envelope", proc.stderr)
                self.assertNotIn("Traceback", proc.stderr)

    def test_R2_deep_nesting_is_an_input_error(self):
        proc = run_cli('{"schema":"acacia.cev/0.1","records":[' + "[" * 100000 + "]" * 100000 + "]}")
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("Traceback", proc.stderr)

    def test_R2_stat_failure_fails_closed(self):
        # e.g. an evidence root without search permission: lstat() raises EACCES.
        with mock.patch.object(pathlib.Path, "is_symlink", side_effect=PermissionError("denied")):
            errors = validate(envelope(record()))
        self.assertTrue(any("unreadable source" in e for e in errors))


class ReviewCoverage(unittest.TestCase):
    """Pass at 28e4f06. Each kills a mutant that survives the PR's own suite."""

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_C_symlinked_source_rejected(self):
        with ScratchRoot() as s:
            (s.root / "AGENTS.md").unlink()
            try:
                (s.root / "AGENTS.md").symlink_to(s.outside)
            except OSError:
                self.skipTest("cannot create symlink here")
            data = envelope(record(evidence=[{"path": "AGENTS.md", "excerpt": TOKEN}]))
            errors = validate(data, root=s.root)
        self.assertTrue(any("missing or symlink source" in e for e in errors))

    def test_C_directory_source_rejected(self):
        with ScratchRoot() as s:
            (s.root / "AGENTS.md").unlink()
            (s.root / "AGENTS.md").mkdir()
            errors = validate(envelope(record(evidence=[{"path": "AGENTS.md", "excerpt": "x"}])), root=s.root)
        self.assertTrue(any("missing or symlink source" in e for e in errors))

    @unittest.skipUnless(hasattr(os, "mkfifo") and hasattr(signal, "SIGALRM"), "FIFOs/SIGALRM unavailable")
    def test_C_fifo_source_rejected_without_blocking(self):
        # If the is_file() guard is bypassed, read_bytes() on a FIFO blocks forever;
        # the alarm turns that hang into a test failure instead of a stuck CI job.
        def _blocked(signum, frame):
            raise TimeoutError("validator blocked opening a FIFO")

        with ScratchRoot() as s:
            (s.root / "AGENTS.md").unlink()
            os.mkfifo(s.root / "AGENTS.md")
            previous = signal.signal(signal.SIGALRM, _blocked)
            signal.alarm(5)
            try:
                errors = validate(envelope(record(evidence=[{"path": "AGENTS.md", "excerpt": "x"}])), root=s.root)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, previous)
        self.assertTrue(any("missing or symlink source" in e for e in errors))

    def test_C_proposal_and_narrative_cannot_be_evidence_checked(self):
        for kind in ("proposal", "historical_narrative"):
            with self.subTest(claim_type=kind):
                errors = validate(envelope(record(claim_type=kind)))
                self.assertTrue(any("cannot be verified as operational fact" in e for e in errors))

    def test_C_verified_status_requires_evidence(self):
        errors = validate(envelope(record(evidence=[])))
        self.assertTrue(any("verified status requires evidence" in e for e in errors))

    def test_C_blank_claim_rejected(self):
        for claim in ("", "   \t", None, 7):
            with self.subTest(claim=claim):
                self.assertTrue(any("missing claim" in e for e in validate(envelope(record(claim=claim)))))

    def test_C_wrong_schema_version_rejected(self):
        self.assertEqual(validate({"schema": "acacia.cev/0.2", "records": []}), ["Invalid CEV envelope"])

    def test_C_empty_excerpt_rejected(self):
        errors = validate(envelope(record(evidence=[{"path": "AUTHORITY.json", "excerpt": ""}])))
        self.assertTrue(any("excerpt absent" in e for e in errors))

    def test_C_non_object_record_rejected(self):
        self.assertTrue(any("records[0]: not an object" in e for e in validate(envelope("record"))))

    def test_C_non_object_evidence_item_rejected(self):
        errors = validate(envelope(record(evidence=["AUTHORITY.json"])))
        self.assertTrue(any("evidence[0]: not an object" in e for e in errors))

    def test_C_evidence_must_be_a_list(self):
        for value in ("AUTHORITY.json", None, {}):
            with self.subTest(evidence=value):
                errors = validate(envelope(record(evidence=value)))
                self.assertTrue(any("evidence must be a list" in e for e in errors))

    def test_C_lookalike_statuses_rejected(self):
        for status in ("independently_verified ", "Independently_Verified", "independently_verified​"):
            with self.subTest(status=ascii(status)):
                self.assertTrue(any("invalid verification" in e
                                    for e in validate(envelope(record(verification=status)))))

    def test_C_allowlist_aliases_rejected(self):
        for path in ("./AGENTS.md", "AGENTS.md/", "agents.md", "/etc/passwd", "AGENTS.md\x00",
                     "research/../AGENTS.md", "ＡGENTS.md"):
            with self.subTest(path=ascii(path)):
                errors = validate(envelope(record(evidence=[{"path": path, "excerpt": "x"}])))
                self.assertTrue(any("not allowlisted" in e for e in errors))

    def test_C_pinned_digest_detects_changed_source(self):
        original = hashlib.sha256((ROOT / "AUTHORITY.json").read_bytes()).hexdigest()
        with ScratchRoot() as s:
            path = s.root / "AUTHORITY.json"
            path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            data = envelope(record(evidence=[{"path": "AUTHORITY.json", "excerpt": "\"schema\"", "sha256": original}]))
            errors = validate(data, root=s.root)
        self.assertTrue(any("sha256 mismatch" in e for e in errors))


class ReviewKnownGaps(unittest.TestCase):
    """Known gaps and protections found at 28e4f06."""

    def test_G_unknown_authority_fields_rejected(self):
        data = envelope(record(keeper_seal="HKX277206", keeper_ruling="approved as Law"))
        self.assertTrue(validate(data), "closed schema: unknown fields should be rejected")

    @unittest.skipUnless(hasattr(os, "link"), "hard links unavailable")
    def test_G_hardlinked_source_rejected(self):
        with ScratchRoot() as s:
            (s.root / "AGENTS.md").unlink()
            os.link(s.outside, s.root / "AGENTS.md")
            errors = validate(envelope(record(evidence=[{"path": "AGENTS.md", "excerpt": TOKEN}])), root=s.root)
        self.assertTrue(errors, "a hard link to a file outside the allowlist was read")

    @unittest.expectedFailure
    def test_G_contradicting_excerpt_not_evidence_checked(self):
        rec = record(claim="AUTHORITY.json grants AI agents authority to merge to main.",
                     evidence=[{"path": "AUTHORITY.json", "excerpt": "Sole authority to merge to main"}])
        self.assertTrue(validate(envelope(rec)), "textual presence is not entailment")

    def test_G_trivial_excerpt_rejected(self):
        rec = record(claim="Claude holds the Keeper Seal.",
                     evidence=[{"path": "AUTHORITY.json", "excerpt": " "}])
        self.assertTrue(validate(envelope(rec)), "a one-byte excerpt supports any claim")


if __name__ == "__main__":
    unittest.main()