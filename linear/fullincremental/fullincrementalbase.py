from linear.linearbase import LinearTestBase
import os

class FullIncrementalTestBase(LinearTestBase):
    def _set_up(self, temp_dir):
        super(FullIncrementalTestBase, self) \
            ._set_up(temp_dir)
        self._build(temp_dir)
        self._wait_for_stamp_update()
        with open(os.path.join(temp_dir, 'file_1'), 'w') \
                as f:
            f.write('new content')
