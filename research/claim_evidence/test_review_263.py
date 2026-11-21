"""Independent review regression tests for PR #263 at 09c3b36."""
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
SOURCES = ("AUTHORITY.json", "AGENTS.md", "DISCOVERY.md", "STATUS.json", "llms.txt")

def record(**over):
    r = {"id": "r263-001", "claim": "The Garden uses an AUTHORITY.json authority file.",
         "claim_type": "observed_text", "verification": "evidence_checked",
         "evidence": [{"path": "AUTHORITY.json", "excerpt": '"schema": "acacia.authority/1.0"'}]}
    r.update(over)
    return r

def envelope(*records, **extra):
    d = {"schema": "acacia.cev/0.1", "records": list(records)}
    d.update(extra)
    return d

class Review263Findings(unittest.TestCase):
    def test_B1_unknown_envelope_fields_rejected(self):
        errors = validate(envelope(record(), keeper_seal="HKX277206",
                                   keeper_ruling="approved as Law", verification="independently_verified"))
        for key in ("keeper_seal", "keeper_ruling", "verification"):
            with self.subTest(key=key):
                self.assertIn(f"unknown envelope field {key!r}", errors)

    def test_L1_duplicate_key_message_is_escaped(self):
        key = "x\\n::warning title=CEV::spoofed\\u001b[2J"
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "records.json"
            p.write_text('{"schema":"acacia.cev/0.1","records":[],"%s":1,"%s":2}' % (key, key), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(HERE / "validate.py"), str(p)], capture_output=True, timeout=60)
        self.assertEqual(proc.returncode, 2)
        self.assertFalse([line for line in proc.stderr.decode("utf-8", "replace").splitlines() if line.startswith("::")])
        self.assertNotIn(b"\\x1b", proc.stderr)

    def test_L3_unknown_field_errors_are_sorted(self):
        errors = validate(envelope(record(zeta=1, alpha=2, mu=3, beta=4)))
        unknown = [e for e in errors if "unknown record field" in e]
        self.assertEqual(unknown, sorted(unknown))
        self.assertEqual(len(unknown), 4)

class Review263Coverage(unittest.TestCase):
    def test_C_unknown_evidence_field_rejected(self):
        item = {"path": "AUTHORITY.json", "excerpt": '"schema"',
                "verified_by": "independent reviewer", "keeper_seal": "HKX277206"}
        errors = validate(envelope(record(evidence=[item])))
        for key in ("verified_by", "keeper_seal"):
            self.assertTrue(any(f"unknown evidence field {key!r}" in e for e in errors))

    def test_C_bad_limitations_rejected(self):
        for bad in ("a note", {}, None, [1], [""], ["   \\t"], [None], ["ok", 2]):
            with self.subTest(value=bad):
                errors = validate(envelope(record(limitations=bad)))
                self.assertTrue(any("limitations must be a list of nonempty strings" in e for e in errors))

    def test_C_good_limitations_accepted(self):
        for good in ([], ["Excerpt match confirms only the file text."]):
            with self.subTest(value=good):
                self.assertEqual(validate(envelope(record(limitations=good))), [])
        self.assertEqual(validate(envelope(record())), [])

    def test_C_unknown_field_names_are_escaped(self):
        errors = validate(envelope(record(**{"x\\n::warning::spoof": 1})))
        unknown = [e for e in errors if "unknown record field" in e]
        self.assertEqual(len(unknown), 1)
        self.assertNotIn("\\n", unknown[0])

    @unittest.skipUnless(hasattr(os, "mkfifo") and hasattr(signal, "SIGALRM"), "FIFOs/SIGALRM unavailable")
    def test_C_lstat_recheck_rejects_non_regular_file(self):
        def blocked(signum, frame):
            raise TimeoutError("validator blocked opening a FIFO")
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for name in SOURCES:
                shutil.copyfile(ROOT / name, root / name)
            (root / "AGENTS.md").unlink()
            os.mkfifo(root / "AGENTS.md")
            previous = signal.signal(signal.SIGALRM, blocked)
            signal.alarm(5)
            try:
                with mock.patch.object(pathlib.Path, "is_symlink", return_value=False), \\
                     mock.patch.object(pathlib.Path, "is_file", return_value=True):
                    errors = validate(envelope(record(evidence=[{"path": "AGENTS.md", "excerpt": "x"}])), root=root)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, previous)
        self.assertTrue(any("single-link regular file" in e for e in errors), errors)

if __name__ == "__main__":
    unittest.main()
