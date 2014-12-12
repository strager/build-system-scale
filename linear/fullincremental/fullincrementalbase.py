import os

class FullIncrementalTestBase(object):
    def _set_up(self, temp_dir):
        super(Test, self)._set_up(temp_dir)
        self._build(temp_dir)
        with open(os.path.join(temp_dir, 'file_1'), 'w') \
                as f:
            f.write('new content')
