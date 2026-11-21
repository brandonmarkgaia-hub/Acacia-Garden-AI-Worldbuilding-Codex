#!/usr/bin/env python3
"""Negative controls for the experimental CEV validator."""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

VALIDATOR = pathlib.Path(__file__).with_name("validate.py")
spec = importlib.util.spec_from_file_location("cev_validator", VALIDATOR)
cev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cev)


class ColdWallTests(unittest.TestCase):
    def run_cli(self, raw):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "records.json"
            path.write_text(raw, encoding="utf-8")
            return subprocess.run([sys.executable, str(VALIDATOR), str(path)],
                                  capture_output=True, text=True)

    def test_duplicate_envelope_key_rejected(self):
        result = self.run_cli('{"schema":"acacia.cev/0.1","schema":"acacia.cev/0.1","records":[]}')
        self.assertEqual(result.returncode, 2)
        self.assertIn("Duplicate JSON key", result.stderr)

    def test_duplicate_verification_key_rejected(self):
        raw = '{"schema":"acacia.cev/0.1","records":[{"id":"x","claim":"x","claim_type":"proposal","verification":"unverified","verification":"evidence_checked","evidence":[]}]}'
        result = self.run_cli(raw)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Duplicate JSON key", result.stderr)

    def test_nonfinite_number_rejected(self):
        self.assertEqual(self.run_cli('{"schema":"acacia.cev/0.1","records":[],"x":NaN}').returncode, 2)

    def test_malformed_json_is_controlled(self):
        self.assertEqual(self.run_cli('{"schema":').returncode, 2)

    def test_valid_empty_envelope(self):
        self.assertEqual(self.run_cli(json.dumps({"schema":"acacia.cev/0.1","records":[]})).returncode, 0)

    def test_symlink_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "actual").write_text("proof", encoding="utf-8")
            (root / "AUTHORITY.json").symlink_to(root / "actual")
            data = {"schema":"acacia.cev/0.1","records":[{
                "id":"x","claim":"proof","claim_type":"observed_text",
                "verification":"evidence_checked",
                "evidence":[{"path":"AUTHORITY.json","excerpt":"proof"}]}]}
            errors = cev.validate(data, root=root)
            self.assertTrue(any("symlink" in error for error in errors), errors)

    def test_invalid_evidence_path_type(self):
        data = {"schema":"acacia.cev/0.1","records":[{
            "id":"x","claim":"x","claim_type":"observed_text",
            "verification":"unverified","evidence":[{"path":["AUTHORITY.json"]}]}]}
        self.assertTrue(cev.validate(data))


if __name__ == "__main__":
    unittest.main()
