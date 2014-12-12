import bsstest
import os
import subprocess

class NinjaTestBase(object):
    name = 'ninja'

    def _build_ninja_path(self, temp_dir):
        return os.path.join(temp_dir, 'build.ninja')

    def _run(self, temp_dir):
        subprocess.check_call([
            'ninja',
            '-j1',
            '-f',
            self._build_ninja_path(temp_dir),
        ], cwd=temp_dir)
