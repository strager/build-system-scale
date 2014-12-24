import bss.dags

class DAGSet(object):
    @staticmethod
    def prepare_parser(arg_parser):
        pass

class LinearDAGSet(DAGSet):
    name = 'Linear'
    variable_label = 'Dependency depth'

    @staticmethod
    def prepare_parser(arg_parser):
        arg_parser.add_argument(
            '--linear-depths',
            dest='linear_depths',
            help='Length of the linear dependency chain',
            metavar='DEPTH',
            nargs='+',
            required=True,
            type=int,
        )

    @staticmethod
    def dags(args):
        for depth in args.linear_depths:
            yield (depth, bss.dags.LinearDAG(depth))

all_dag_sets = [
    LinearDAGSet,
]
