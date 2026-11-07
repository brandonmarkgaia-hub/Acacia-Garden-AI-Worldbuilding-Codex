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
