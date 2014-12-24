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
    @staticmethod
    def name(args):
        return 'Clean'

    @staticmethod
    def set_up(temp_dir, dag, builder, build_nodes, args):
        for node in dag.leaf_nodes():
            dirty_node(node, temp_dir=temp_dir)

class FixedIncrementalSetup(Setup):
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
        # HACK(strager): This only works for LinearDAG.
        assert dag.__class__.__name__ == 'LinearDAG'
        all_nodes = sorted(frozenset(dag.all_nodes())
            - frozenset(dag.leaf_nodes()))
        return (all_nodes[i] for i in xrange(0, min(
            len(all_nodes),
            args.incremental_count,
        )))

class FullIncrementalSetup(Setup):
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
