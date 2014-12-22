from linear.linearbase import LinearTestBase
import os
import sys

class FixedIncrementalTestBase(LinearTestBase):
    def __init__(self, depth, incremental_depth):
        super(FixedIncrementalTestBase, self) \
            .__init__(depth)
        self._incremental_depth = incremental_depth

    @staticmethod
    def default_inputs():
        argv = sys.argv[1:]
        incremental_depth = int(argv[0])
        return [
            (int(arg), incremental_depth)
            for arg in argv[1:]
        ]

    fields = ('depth', 'incremental_depth')

    @property
    def inputs(self):
        return (self._depth, self._incremental_depth)

    def _set_up(self, temp_dir):
        super(FixedIncrementalTestBase, self) \
            ._set_up(temp_dir)
        self._build(temp_dir)
        self._wait_for_stamp_update()
        name = 'file_{}'.format(
            self._depth - self._incremental_depth,
        )
        with open(os.path.join(temp_dir, name), 'w') as f:
            f.write('new content')
