from lib.bsstest import BSSTest
import os
import sys

class LinearTestBase(BSSTest):
    def __init__(self, depth):
        super(LinearTestBase, self).__init__()
        self._depth = depth

    @classmethod
    def _augment_arg_parser(cls, arg_parser):
        super(LinearTestBase, cls) \
            ._augment_arg_parser(arg_parser)
        if arg_parser.has_action('depths'):
            return
        arg_parser.add_argument(
            'depths',
            help='Length of the linear dependency chain',
            metavar='DEPTH',
            nargs='+',
            type=int,
        )

    @staticmethod
    def default_inputs(args):
        return [(arg,) for arg in args.depths]

    fields = ('depth',)

    @property
    def inputs(self):
        return (self._depth,)

    def _set_up(self, temp_dir):
        f_path = os.path.join(temp_dir, 'file_1')
        with open(f_path, 'wb') as f:
            f.write('hello world')
