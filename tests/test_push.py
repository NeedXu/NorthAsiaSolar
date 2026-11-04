import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/push-main.sh'
class PushRecoveryTests(unittest.TestCase):
    def test_transient_rejection_and_concurrent_commit_are_recovered_without_force(self):
        def git(cwd,*args):
            return subprocess.run(['git',*args],cwd=cwd,check=True,capture_output=True,text=True).stdout.strip()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            remote=root/'remote.git'; a=root/'writer'; b=root/'other'
            git(root,'init','--bare','--initial-branch=main',str(remote))
            git(root,'clone',str(remote),str(a))
            for repo in [a]:
                git(repo,'config','user.name','Integration Test');git(repo,'config','user.email','test@example.invalid')
            (a/'initial').write_text('initial')
            git(a,'add','.');git(a,'commit','-m','initial');git(a,'push','origin','HEAD:main')
            git(root,'clone',str(remote),str(b))
            git(b,'config','user.name','Integration Test');git(b,'config','user.email','test@example.invalid')
            (b/'concurrent').write_text('preserve this remote work')
            git(b,'add','.');git(b,'commit','-m','concurrent');git(b,'push','origin','HEAD:main')
            (a/'state').write_text('enabled')
            git(a,'add','.');git(a,'commit','-m','update state')
            hook=remote/'hooks'/'pre-receive'
            hook.write_text('#!/bin/sh\nif [ ! -f retry-tested ]; then touch retry-tested; echo "simulated commit_refs failure" >&2; exit 1; fi\nexit 0\n')
            hook.chmod(0o755)
            result=subprocess.run(['bash',str(SCRIPT)],cwd=a,capture_output=True,text=True,timeout=45)
            self.assertEqual(result.returncode,0,result.stderr)
            git(a,'fetch','origin','main')
            self.assertEqual(git(a,'rev-parse','HEAD'),git(a,'rev-parse','origin/main'))
            self.assertEqual((a/'concurrent').read_text(),'preserve this remote work')
            self.assertEqual((a/'state').read_text(),'enabled')
