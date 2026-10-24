"""Regression: a changed immutable founder record must fail closed."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.guard_immutable_authority import check

class ImmutableAuthorityGuardTests(unittest.TestCase):
    def test_rejects_tampered_founder_and_accepts_original(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            subprocess.run(["git","init","-q",str(repo)],check=True)
            original = json.loads(Path("AUTHORITY.json").read_text(encoding="utf-8"))
            (repo/"AUTHORITY.json").write_text(json.dumps(original),encoding="utf-8")
            subprocess.run(["git","-C",str(repo),"add","AUTHORITY.json"],check=True)
            subprocess.run(["git","-C",str(repo),"-c","user.name=Test","-c","user.email=test@example.invalid","commit","-qm","baseline"],check=True)
            import os
            old=os.getcwd()
            try:
                os.chdir(repo)
                self.assertEqual(check("HEAD"),0)
                modified=json.loads((repo/"AUTHORITY.json").read_text())
                modified["immutable_record"]["founder"]["name"]="TAMPERED FOUNDER"
                (repo/"AUTHORITY.json").write_text(json.dumps(modified))
                self.assertEqual(check("HEAD"),1)
                modified.pop("immutable_record")
                (repo/"AUTHORITY.json").write_text(json.dumps(modified))
                self.assertEqual(check("HEAD"),1)
            finally:
                os.chdir(old)

if __name__=="__main__":
    unittest.main()
