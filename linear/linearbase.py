from lib.bsstest import BSSTest
import os
import sys

class LinearTestBase(BSSTest):
    def __init__(self, depth):
        super(LinearTestBase, self).__init__()
        self._depth = depth

    @staticmethod
    def default_inputs():
        return [(int(arg),) for arg in sys.argv[1:]]

    fields = ('depth',)

    @property
    def inputs(self):
        return (self._depth,)

    def _set_up(self, temp_dir):
        f_path = os.path.join(temp_dir, 'file_1')
        with open(f_path, 'wb') as f:
            f.write('hello world')
