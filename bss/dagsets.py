import bss.dags

class DAGSet(object):
    @staticmethod
    def prepare_parser(arg_parser):
        pass

class FanOutDAGSet(DAGSet):
    name = 'Uniform Fan-Out'
    variable_label = 'Fan-Out (Edges)'

    @staticmethod
    def prepare_parser(arg_parser):
        arg_parser.add_argument(
            '--fan-out-edges',
            dest='fan_out_edges',
            help='Width of the dependency graph',
            metavar='EDGES',
            nargs='+',
            required=False,
            type=int,
        )

    @staticmethod
    def dags(args):
        if args.fan_out_edges is None:
            return
        depth = 2
        for fan_out in args.fan_out_edges:
            yield (fan_out, bss.dags.UniformFanOutDAG(
                depth=depth,
                fan_out=fan_out,
            ))

class LinearDAGSet(DAGSet):
    name = 'Linear'
    variable_label = 'Dependency Depth'

    @staticmethod
    def prepare_parser(arg_parser):
        arg_parser.add_argument(
            '--linear-depths',
            dest='linear_depths',
            help='Length of the linear dependency chain',
            metavar='DEPTH',
            nargs='+',
            required=False,
            type=int,
        )

    @staticmethod
    def dags(args):
        if args.linear_depths is None:
            return
        for depth in args.linear_depths:
            yield (depth, bss.dags.LinearDAG(depth))

all_dag_sets = [
    FanOutDAGSet,
    LinearDAGSet,
]
