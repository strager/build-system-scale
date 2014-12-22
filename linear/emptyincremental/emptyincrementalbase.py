from linear.linearbase import LinearTestBase
import os

class EmptyIncrementalTestBase(LinearTestBase):
    title = 'Linear Empty Incremental'

    def _set_up(self, temp_dir):
        super(EmptyIncrementalTestBase, self) \
            ._set_up(temp_dir)
        self._build(temp_dir)
