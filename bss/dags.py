#!/usr/bin/env python2.7

import collections
import itertools
import re
import subprocess
import sys
import tempfile
import unittest

def validate_dag(dag):
    all_nodes = frozenset(dag.all_nodes())
    leaf_nodes = frozenset(dag.leaf_nodes())
    root_nodes = frozenset(dag.root_nodes())
    visited_nodes = set()
    queue = set(root_nodes)
    while queue:
        node = queue.pop()
        assert node in all_nodes
        assert node not in visited_nodes
        visited_nodes.add(node)
        edge_nodes = frozenset(dag.nodes_from(node))
        if edge_nodes:
            assert node not in leaf_nodes
            for edge_node in edge_nodes:
                assert edge_node not in root_nodes
                assert edge_node in all_nodes
                if edge_node not in visited_nodes:
                    queue.add(edge_node)
        else:
            assert node in leaf_nodes, \
                'Expected {} in leaf_nodes'.format(node)

def dag_png(dag, output_file_path):
    with tempfile.NamedTemporaryFile('w') as temp_file:
        dag_dot(dag, temp_file)
        temp_file.flush()
        subprocess.check_call([
            'dot',
            '-Tpng',
            '-o{}'.format(output_file_path),
            temp_file.name,
        ])

def dag_dot(dag, output_file):
    output_file.write('digraph dag {\n')
    for (from_node, to_nodes) in dag.flatten():
        for to_node in to_nodes:
            output_file.write(
                '  {} -> {};\n'.format(from_node, to_node),
            )
        else:
            output_file.write('  {};\n'.format(from_node))
    output_file.write('}\n')

class DAG(object):
    def __eq__(self, other):
        self_nodes = frozenset(self.all_nodes())
        if self_nodes != frozenset(other.all_nodes()):
            return False
        for node in self_nodes:
            if frozenset(self.nodes_from(node)) \
                    != frozenset(other.nodes_from(node)):
                return False
        return True

    def nodes_to(self, node):
        for test_node in frozenset(self.all_nodes()):
            if node in self.nodes_from(test_node):
                yield test_node

    def dump(self, file=sys.stdout):
        file.write('Dump of {}:\n'.format(self))
        file.write('  root_nodes() = {}\n'.format(
            ' '.join(map(str, self.root_nodes())),
        ))
        file.write('  leaf_nodes() = {}\n'.format(
            ' '.join(map(str, self.leaf_nodes())),
        ))
        for (from_node, to_nodes) in self.flatten():
            file.write('  {} -> {}\n'.format(
                from_node,
                ' '.join(map(str, to_nodes)),
            ))

    def flatten(self, starting_nodes=None):
        if starting_nodes is None:
            starting_nodes = self.root_nodes()
        visited_nodes = set()
        queue = set(starting_nodes)
        while queue:
            node = queue.pop()
            visited_nodes.add(node)
            to_nodes = frozenset(self.nodes_from(node))
            yield (node, to_nodes)
            for to_node in to_nodes:
                if to_node not in visited_nodes:
                    queue.add(to_node)

    def all_nodes_sorted_topologically(self):
        # Algorithm borrowed from @ovgolovin:
        # http://stackoverflow.com/a/15039202
        # Licensed under CC BY-SA 3.0:
        # http://creativecommons.org/licenses/by-sa/3.0/

        levels_by_name = {}
        names_by_level = collections.defaultdict(set)

        def add_level_to_name(name, level):
            levels_by_name[name] = level
            names_by_level[level].add(name)

        def walk_depth_first(name):
            stack = [name]
            while stack:
                name = stack.pop()
                if name in levels_by_name:
                    continue

                children = frozenset(self.nodes_from(name))
                if not children:
                    level = 0
                    add_level_to_name(name, level)
                    continue

                children_not_calculated = [
                    child for child in children
                    if child not in levels_by_name
                ]
                if children_not_calculated:
                    stack.append(name)
                    stack.extend(children_not_calculated)
                    continue

                level = 1 + max(
                    levels_by_name[lname]
                    for lname in children
                )
                add_level_to_name(name, level)

        for name in self.all_nodes():
            walk_depth_first(name)

        return list(itertools.takewhile(
            lambda x: x is not None,
            (
                names_by_level.get(i, None)
                for i in itertools.count()
            )
        ))

class DotDAG(DAG):
    '''
    DAG generated from a Graphviz DOT file.
    '''
    __ignore_re = re.compile(
        r'^(?:'
         'digraph ninja \{'
         '|\}'
         '|rankdir=.*'
         '|(?:node|edge) .*'
         '|node .*'
         ')$'
    )
    __node_re = re.compile(r'^\s*(\S+)(?:\s+\[.*\])?\s*$')
    __edge_re = re.compile(
        r'^\s*(\S+)\s+->\s+(\S+)(?:\s+\[.*\])?\s*$',
    )

    def __init__(self, dot_path):
        current_node = [0]
        def new_node():
            current_node[0] += 1
            return current_node[0]

        node_string_nodes \
            = collections.defaultdict(new_node)
        edges_from = collections.defaultdict(set)
        not_leaf_nodes = set()
        not_root_nodes = set()

        # This parser is hacky.  It only works well on
        # Ninja-generated DOT files.
        with file(dot_path, 'r') as dot_file:
            for line in dot_file:
                if DotDAG.__ignore_re.match(line):
                    # Skip ignored lines.
                    continue
                match = DotDAG.__node_re.match(line)
                if match:
                    node = node_string_nodes[match.group(1)]
                    edges_from[node]  # Tickle defaultdict.
                    continue
                match = DotDAG.__edge_re.match(line)
                if match:
                    to_node \
                        = node_string_nodes[match.group(1)]
                    from_node \
                        = node_string_nodes[match.group(2)]
                    edges_from[from_node].add(to_node)
                    not_leaf_nodes.add(from_node)
                    not_root_nodes.add(to_node)
                    continue
                raise Exception(
                    'Parse error: {}'.format(line),
                )

        self.__all_nodes \
            = frozenset(node_string_nodes.values())
        self.__root_nodes \
            = frozenset(self.__all_nodes - not_root_nodes)
        self.__leaf_nodes \
            = frozenset(self.__all_nodes - not_leaf_nodes)
        self.__edges_from = {
            from_node: frozenset(to_nodes)
            for (from_node, to_nodes)
            in edges_from.iteritems()
        }

        validate_dag(self)

    def root_nodes(self):
        return self.__root_nodes

    def leaf_nodes(self):
        return self.__leaf_nodes

    def all_nodes(self):
        return self.__all_nodes

    def nodes_from(self, node):
        return self.__edges_from[node]

class LinearDAG(DAG):
    def __init__(self, depth):
        self.__depth = depth

    def root_nodes(self):
        return [1]

    def leaf_nodes(self):
        return [self.__depth]

    def all_nodes(self):
        return xrange(1, self.__depth + 1)

    def nodes_from(self, node):
        assert node in self.all_nodes()
        if node == self.__depth:
            return []
        else:
            return [node + 1]

class UniformFanOutDAG(DAG):
    '''
    UniformFanOutDAG(depth=4, fan_out=2) creates the
    following DAG:

    leaves: [8, 9, 10, 11, 12, 13, 14, 15]
    roots: [1]

    # Second level
    1 -> 2
    1 -> 3

    # Third level
    2 -> 4
    2 -> 5
    3 -> 6
    3 -> 7

    # Fourth level
    4 -> 8
    4 -> 9
    5 -> 10
    5 -> 11
    6 -> 12
    6 -> 13
    7 -> 14
    7 -> 15
    '''

    def __init__(self, depth, fan_out):
        self.__depth = depth
        self.__fan_out = fan_out

    def root_nodes(self):
        return [1]

    @staticmethod
    def node_count(depth, fan_out):
        if fan_out == 1:
            return depth
        else:
            return (fan_out ** depth - 1) / (fan_out - 1)

    def __nodes_at_depth(self, depth):
        return UniformFanOutDAG.node_count(
            depth=depth,
            fan_out=self.__fan_out,
        )

    def leaf_nodes(self):
        return xrange(
            self.__nodes_at_depth(self.__depth - 1) + 1,
            self.__nodes_at_depth(self.__depth) + 1,
        )

    def all_nodes(self):
        return xrange(
            1,
            self.__nodes_at_depth(self.__depth) + 1,
        )

    def __first_child(self, node):
        return node * self.__fan_out - self.__fan_out + 2

    def nodes_from(self, node):
        assert node in self.all_nodes()
        if node in self.leaf_nodes():
            return []
        else:
            return xrange(
                self.__first_child(node),
                self.__first_child(node + 1),
            )

class TestUniformFanOutDAG(unittest.TestCase):
    def test_fan_out1_equals_linear(self):
        for depth in xrange(1, 10):
            dag = UniformFanOutDAG(depth=depth, fan_out=1)
            linear_dag = LinearDAG(depth=depth)
            self.assertEqual(dag, linear_dag)
            validate_dag(dag)
            validate_dag(linear_dag)

    def test_fan_out1_is_linear(self):
        for depth in xrange(1, 10):
            dag = UniformFanOutDAG(depth=depth, fan_out=1)
            node = dag.root_nodes()[0]
            while True:
                nodes = list(dag.nodes_from(node))
                if not nodes:
                    break
                self.assertItemsEqual(nodes, [node + 1])
                node = nodes[0]
            validate_dag(dag)

    def test_depth1(self):
        for fan_out in xrange(1, 10):
            dag = UniformFanOutDAG(depth=1, fan_out=fan_out)
            self.assertItemsEqual(dag.root_nodes(), [1])
            self.assertItemsEqual(dag.all_nodes(), [1])
            self.assertItemsEqual(dag.leaf_nodes(), [1])
            self.assertItemsEqual(dag.nodes_from(1), [])
            validate_dag(dag)

    def test_depth2_fan_out_2(self):
        dag = UniformFanOutDAG(depth=2, fan_out=2)
        self.assertItemsEqual(dag.all_nodes(), [1, 2, 3])
        validate_dag(dag)

    def test_depth3_fan_out_2(self):
        dag = UniformFanOutDAG(depth=3, fan_out=2)
        self.assertItemsEqual(
            dag.all_nodes(),
            [1, 2, 3, 4, 5, 6, 7],
        )
        validate_dag(dag)

    def test_depth4_fan_out_2(self):
        dag = UniformFanOutDAG(depth=4, fan_out=2)
        self.assertItemsEqual(dag.root_nodes(), [1])
        self.assertItemsEqual(
            dag.all_nodes(),
            xrange(1, 16),
        )
        self.assertItemsEqual(
            dag.leaf_nodes(),
            xrange(8, 16),
        )
        self.assertItemsEqual(dag.nodes_from(1), [2, 3])
        self.assertItemsEqual(dag.nodes_from(2), [4, 5])
        self.assertItemsEqual(dag.nodes_from(3), [6, 7])
        self.assertItemsEqual(dag.nodes_from(4), [8, 9])
        self.assertItemsEqual(dag.nodes_from(5), [10, 11])
        self.assertItemsEqual(dag.nodes_from(6), [12, 13])
        self.assertItemsEqual(dag.nodes_from(7), [14, 15])
        self.assertItemsEqual(dag.nodes_from(8), [])
        self.assertItemsEqual(dag.nodes_from(9), [])
        self.assertItemsEqual(dag.nodes_from(10), [])
        self.assertItemsEqual(dag.nodes_from(11), [])
        self.assertItemsEqual(dag.nodes_from(12), [])
        self.assertItemsEqual(dag.nodes_from(13), [])
        self.assertItemsEqual(dag.nodes_from(14), [])
        self.assertItemsEqual(dag.nodes_from(15), [])
        validate_dag(dag)

    def test_depth2_fan_out_3(self):
        dag = UniformFanOutDAG(depth=2, fan_out=3)
        self.assertItemsEqual(dag.all_nodes(), [1, 2, 3, 4])

    def test_depth3_fan_out_3(self):
        dag = UniformFanOutDAG(depth=3, fan_out=3)
        self.assertItemsEqual(dag.root_nodes(), [1])
        self.assertItemsEqual(
            dag.all_nodes(),
            xrange(1, 14),
        )
        self.assertItemsEqual(
            dag.leaf_nodes(),
            xrange(5, 14),
        )
        self.assertItemsEqual(dag.nodes_from(1), [2, 3, 4])
        self.assertItemsEqual(dag.nodes_from(2), [5, 6, 7])
        self.assertItemsEqual(dag.nodes_from(3), [8, 9, 10])
        self.assertItemsEqual(
            dag.nodes_from(4),
            [11, 12, 13],
        )
        self.assertItemsEqual(dag.nodes_from(5), [])
        self.assertItemsEqual(dag.nodes_from(6), [])
        self.assertItemsEqual(dag.nodes_from(7), [])
        self.assertItemsEqual(dag.nodes_from(8), [])
        self.assertItemsEqual(dag.nodes_from(9), [])
        self.assertItemsEqual(dag.nodes_from(10), [])
        self.assertItemsEqual(dag.nodes_from(11), [])
        self.assertItemsEqual(dag.nodes_from(12), [])
        self.assertItemsEqual(dag.nodes_from(13), [])
        validate_dag(dag)

class TestLinearDAG(unittest.TestCase):
    def test_topological_sort_10(self):
        dag = LinearDAG(10)
        self.assertEqual(
            dag.all_nodes_sorted_topologically(),
            [{i} for i in xrange(10, 0, -1)],
        )

    def test_topological_sort_10000(self):
        dag = LinearDAG(10000)
        self.assertEqual(
            dag.all_nodes_sorted_topologically(),
            [{i} for i in xrange(10000, 0, -1)],
        )

if __name__ == '__main__':
    unittest.main()
