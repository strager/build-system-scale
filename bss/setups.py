import os

__dirty_iteration = 0

def node_path(node, temp_dir):
    return os.path.join(temp_dir, str(node))

def dirty_node(node, temp_dir):
    global __dirty_iteration
    __dirty_iteration += 1
    # N.B. The file size must be the same regardless of
    # inputs.  Otherwise timings may be affected.
    contents = '{:020}; {:020}'.format(
        __dirty_iteration,
        node,
    )
    assert len(contents) == 42

    with file(node_path(node, temp_dir), 'wb') as f:
        f.write(contents)

class Setup(object):
    @staticmethod
    def prepare_parser(arg_parser):
        pass

class CleanSetup(Setup):
    shortname = 'clean'

    @staticmethod
    def name(args):
        return 'Clean'

    @staticmethod
    def set_up(temp_dir, dag, builder, build_nodes, args):
        for node in dag.leaf_nodes():
            dirty_node(node, temp_dir=temp_dir)

class FixedIncrementalSetup(Setup):
    shortname = 'fixed-incremental'

    @staticmethod
    def name(args):
        return '{} (Fixed) Incremental'.format(
            args.incremental_count,
        )

    @staticmethod
    def prepare_parser(arg_parser):
        arg_parser.add_argument(
            '--incremental-count',
            dest='incremental_count',
            help='Number of targets to require rebuilding',
            metavar='INTEGER',
            required=True,
            type=int,
        )

    @staticmethod
    def set_up(temp_dir, dag, builder, build_nodes, args):
        CleanSetup.set_up(
            temp_dir=temp_dir,
            dag=dag,
            builder=builder,
            build_nodes=build_nodes,
            args=args,
        )
        builder.build(
            temp_dir=temp_dir,
            nodes=build_nodes,
            args=args,
        )
        builder.wait_for_stamp_update()
        for node in FixedIncrementalSetup \
                .__dirty_nodes(
                    args=args,
                    build_nodes=build_nodes,
                    dag=dag,
                ):
            os.remove(node_path(node, temp_dir=temp_dir))

    @staticmethod
    def __dirty_nodes(args, build_nodes, dag):
        dirty_node_count = args.incremental_count
        if dirty_node_count <= 0:
            return []

        # We cannot dirty leaf nodes.
        leaves = frozenset(dag.leaf_nodes())

        # Mark build_nodes as dirty.
        dirty_nodes = set()
        for node in build_nodes:
            if node in leaves:
                continue
            dirty_nodes.add(node)
            if len(dirty_nodes) == dirty_node_count:
                return dirty_nodes

        # Mark dependencies of build_nodes as dirty, and
        # their dependencies, and so on.
        queue = list(dirty_nodes)
        while queue:
            node = queue.pop()
            if node in leaves:
                continue
            pointers = frozenset(dag.nodes_to(node))
            if pointers - dirty_nodes:
                # If we mark node as dirty, it would cause
                # nodes we haven't marked dirty yet to be
                # implicitly dirty (in the build system),
                # but only if you can trace them back to any
                # of build_nodes.
                raise NotImplementedError()
            dirty_nodes.add(node)
            if len(dirty_nodes) == dirty_node_count:
                return dirty_nodes
            queue.extend(dag.nodes_from(node))

        assert dirty_nodes \
            == frozenset(dag.all_nodes()) - leaves
        return dirty_nodes

class FullIncrementalSetup(Setup):
    shortname = 'full-incremental'

    @staticmethod
    def name(args):
        return 'Full Incremental'

    @staticmethod
    def set_up(temp_dir, dag, builder, build_nodes, args):
        CleanSetup.set_up(
            temp_dir=temp_dir,
            dag=dag,
            builder=builder,
            build_nodes=build_nodes,
            args=args,
        )
        builder.build(
            temp_dir=temp_dir,
            nodes=build_nodes,
            args=args,
        )
        builder.wait_for_stamp_update()
        for node in dag.leaf_nodes():
            dirty_node(node, temp_dir=temp_dir)

class NoOpIncrementalSetup(Setup):
    shortname = 'empty-incremental'

    @staticmethod
    def name(args):
        return 'Empty Incremental'

    @staticmethod
    def set_up(temp_dir, dag, builder, build_nodes, args):
        CleanSetup.set_up(
            temp_dir=temp_dir,
            dag=dag,
            builder=builder,
            build_nodes=build_nodes,
            args=args,
        )
        builder.build(
            temp_dir=temp_dir,
            nodes=build_nodes,
            args=args,
        )
        builder.wait_for_stamp_update()

all_setups = [
    CleanSetup,
    FixedIncrementalSetup,
    FullIncrementalSetup,
    NoOpIncrementalSetup,
]
