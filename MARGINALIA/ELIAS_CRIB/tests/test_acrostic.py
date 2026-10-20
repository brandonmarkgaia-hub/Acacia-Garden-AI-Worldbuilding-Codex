import unittest
from pathlib import Path

class AcrosticTest(unittest.TestCase):
    def test_marker(self):
        text = (Path(__file__).resolve().parents[1] / 'EASTER_EGG.md').read_text()
        assert 'The First Apple' in text
        assert 'non-evidentiary' in text.lower()
