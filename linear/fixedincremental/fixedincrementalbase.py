from linear.linearbase import LinearTestBase
import os
import sys

class FixedIncrementalTestBase(LinearTestBase):
    def __init__(self, depth, incremental_depth):
        super(FixedIncrementalTestBase, self) \
            .__init__(depth)
        self._incremental_depth = incremental_depth

    @classmethod
    def _augment_arg_parser(cls, arg_parser):
        super(FixedIncrementalTestBase, cls) \
            ._augment_arg_parser(arg_parser)
        if arg_parser.has_action('incremental_depth'):
            return
        arg_parser.add_argument(
            '--incremental-depth',
            dest='incremental_depth',
            help='Number of targets to invalidate',
            metavar='DEPTH',
            required=True,
            type=int,
        )

    @staticmethod
    def default_inputs(args):
        incremental_depth = args.incremental_depth
        return [
            (arg, incremental_depth)
            for arg in args.depths
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
