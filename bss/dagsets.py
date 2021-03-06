import bss.dags
import itertools
import logging
import os
import sys

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stderr))

_data_dir = os.path.join(
    os.path.dirname(__file__),
    '..',
    'data',
)

class DAGSet(object):
    @staticmethod
    def prepare_parser(arg_parser):
        pass

class ChromiumDAGSet(DAGSet):
    name = 'Chromium (from GYP+Ninja)'
    shortname = 'chromium'
    variable_label = 'N/A'

    @staticmethod
    def dags(args):
        yield (0, bss.dags.DotDAG(
            os.path.join(_data_dir, 'chromium.dot'),
        ))

class FanOutDAGSet(DAGSet):
    name = 'Fan-Out'
    shortname = 'fan-out'
    variable_label = 'Fan-Out (Edges)'

    @staticmethod
    def prepare_parser(arg_parser):
        arg_parser.add_argument(
            '--fan-out-edges',
            dest='fan_out_edges',
            help='Width of the dependency graph',
            metavar='EDGES',
            nargs='+',
            required=True,
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

class LLVMDAGSet(DAGSet):
    name = 'LLVM (from CMake+Ninja)'
    shortname = 'llvm'
    variable_label = 'N/A'

    @staticmethod
    def dags(args):
        yield (0, bss.dags.DotDAG(
            os.path.join(_data_dir, 'llvm.dot'),
        ))

class LinearDAGSet(DAGSet):
    name = 'Linear'
    shortname = 'linear'
    variable_label = 'Dependency Depth'

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
        if args.linear_depths is None:
            return
        for depth in args.linear_depths:
            yield (depth, bss.dags.LinearDAG(depth))

class UniformFanOutDAGSet(DAGSet):
    name = 'Uniform Fan-Out'
    shortname = 'uniform-fan-out'
    variable_label = 'Total Nodes'

    @staticmethod
    def __parse_dag(value):
        node_count = int(value)
        for i in itertools.count(1):
            cur_node_count = bss.dags.UniformFanOutDAG \
                .node_count(i, i)
            if cur_node_count == node_count:
                return (
                    node_count,
                    bss.dags.UniformFanOutDAG(i, i),
                )
            elif cur_node_count < node_count:
                continue
            else:
                logger.warning((
                    'Node count {} invalid; '
                    'choosing {} instead'
                ).format(node_count, cur_node_count))
                return (
                    cur_node_count,
                    bss.dags.UniformFanOutDAG(i - 1, i - 1),
                )

    @staticmethod
    def prepare_parser(arg_parser):
        arg_parser.add_argument(
            '--fan-out-nodes',
            dest='fan_out_dags',
            help='Number of nodes in the graph',
            metavar='NODES',
            nargs='+',
            required=True,
            type=UniformFanOutDAGSet.__parse_dag,
        )

    @staticmethod
    def dags(args):
        if args.fan_out_dags is None:
            return
        for (node_count, dag) in args.fan_out_dags:
            yield (node_count, dag)

all_dag_sets = [
    ChromiumDAGSet,
    FanOutDAGSet,
    LLVMDAGSet,
    LinearDAGSet,
    UniformFanOutDAGSet,
]
