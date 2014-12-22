import bsstest
import os
import subprocess

class GNUMakeTestBase(bsstest.BSSTest):
    name = 'gnumake'

    def _makefile_path(self, temp_dir):
        return os.path.join(temp_dir, 'GNUMakefile')

    def _build(self, temp_dir):
        subprocess.check_call([
            'make',
            '-j1',
            '-f',
            self._makefile_path(temp_dir),
        ], cwd=temp_dir)

    def _run(self, temp_dir):
        self._build(temp_dir)
