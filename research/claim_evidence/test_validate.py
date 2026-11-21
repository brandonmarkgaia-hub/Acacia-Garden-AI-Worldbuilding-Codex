import copy
import json
import pathlib
import unittest
from validate import validate

HERE = pathlib.Path(__file__).resolve().parent


class TestCEV(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((HERE / "examples.json").read_text())

    def test_valid_fixture(self):
        self.assertEqual(validate(self.data), [])

    def test_fabricated_excerpt_rejected(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["evidence"][0]["excerpt"] = "imaginary parser exists"
        self.assertTrue(any("excerpt absent" in e for e in validate(data)))

    def test_traversal_rejected(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["evidence"][0]["path"] = "../../.git/config"
        self.assertTrue(any("not allowlisted" in e for e in validate(data)))

    def test_unsubstantiated_verification_rejected(self):
        data = copy.deepcopy(self.data)
        data["records"][1]["verification"] = "independently_verified"
        self.assertTrue(validate(data))

    def test_independence_not_self_attestable(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["verification"] = "independently_verified"
        self.assertTrue(any("independent verification unsupported" in e for e in validate(data)))

    def test_malformed_types_fail_closed(self):
        for field in ("claim_type", "verification"):
            for bad in ([], {}, 7, None):
                with self.subTest(field=field, bad=bad):
                    data = copy.deepcopy(self.data)
                    data["records"][0][field] = bad
                    self.assertTrue(validate(data))

    def test_malformed_digest_rejected(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["evidence"][0]["sha256"] = []
        self.assertTrue(any("sha256 mismatch" in e for e in validate(data)))

    def test_unreadable_source_fails_closed(self):
        from unittest.mock import patch
        data = copy.deepcopy(self.data)
        with patch.object(pathlib.Path, "read_bytes", side_effect=PermissionError("denied")):
            errors = validate(data)
        self.assertTrue(any("unreadable source" in e for e in errors))

    def test_duplicate_ids_rejected(self):
        data = copy.deepcopy(self.data)
        data["records"][1]["id"] = data["records"][0]["id"]
        self.assertTrue(any("duplicate id" in e for e in validate(data)))

    def test_wrong_hash_rejected(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["evidence"][0]["sha256"] = "0" * 64
        self.assertTrue(any("sha256 mismatch" in e for e in validate(data)))


if __name__ == "__main__":
    unittest.main()
