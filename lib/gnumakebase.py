import bsstest
import os
import subprocess

class GNUMakeTestBase(object):
    name = 'gnumake'

    def _makefile_path(self, temp_dir):
        return os.path.join(temp_dir, 'GNUMakefile')

    def _run(self, temp_dir):
        subprocess.check_call([
            'make',
            '-j1',
            '-f',
            self._makefile_path(temp_dir),
        ], cwd=temp_dir)
