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

class LinearDAG(object):
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
