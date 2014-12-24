#!/usr/bin/env python2.7

import itertools
import os
import subprocess
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
    visited_nodes = set()
    queue = set(dag.root_nodes())
    while queue:
        node = queue.pop()
        for edge_node in dag.nodes_from(node):
            output_file.write(
                '  {} -> {};\n'.format(node, edge_node),
            )
            if edge_node not in visited_nodes:
                queue.add(edge_node)
        else:
            output_file.write('  {};\n'.format(node))
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

    def __nodes_at_depth(self, depth):
        fan_out = self.__fan_out
        if fan_out == 1:
            return depth
        else:
            return (fan_out ** depth - 1) / (fan_out - 1)

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

if __name__ == '__main__':
    unittest.main()
