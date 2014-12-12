import os

class EmptyIncrementalTestBase(object):
    def _set_up(self, temp_dir):
        super(Test, self)._set_up(temp_dir)
        self._build(temp_dir)
