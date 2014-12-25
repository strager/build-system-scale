import bss.util
import os
import subprocess

class Builder(object):
    @staticmethod
    def prepare_parser(arg_parser):
        pass

    @staticmethod
    def wait_for_stamp_update():
        pass

class GNUMakeBuilder(Builder):
    name = 'GNU Make'

    @staticmethod
    def __makefile_path(temp_dir):
        return os.path.join(temp_dir, 'GNUMakefile')

    @staticmethod
    def set_up(temp_dir, dag, args):
        makefile_path \
            = GNUMakeBuilder.__makefile_path(temp_dir)
        with open(makefile_path, 'w') as makefile:
            for from_node in dag.all_nodes():
                to_nodes = list(dag.nodes_from(from_node))
                if to_nodes:
                    makefile.write(
                       '{}: {}\n\t@cat $^ >$@\n'.format(
                            from_node,
                            ' '.join(map(str, to_nodes)),
                        ),
                    )

    @staticmethod
    def build(temp_dir, nodes, args):
        subprocess.check_call([
            'make',
            '-j1',
            '-f',
            GNUMakeBuilder.__makefile_path(temp_dir),
        ] + map(str, nodes), cwd=temp_dir)

    @staticmethod
    def wait_for_stamp_update():
        bss.util.wait_for_temp_file_system_stamp_update()

class NinjaBuilder(Builder):
    name = 'Ninja'

    @staticmethod
    def __build_ninja_path(temp_dir):
        return os.path.join(temp_dir, 'build.ninja')

    @staticmethod
    def set_up(temp_dir, dag, args):
        build_ninja_path \
            = NinjaBuilder.__build_ninja_path(temp_dir)
        with open(build_ninja_path, 'w') as ninja:
            ninja.write('ninja_required_version = 1.0\n')
            ninja.write(
                'rule cp\n command = cat $in >$out\n',
            )
            for from_node in dag.all_nodes():
                to_nodes = list(dag.nodes_from(from_node))
                if to_nodes:
                    to_node_list \
                        = ' '.join(map(str, to_nodes))
                    ninja.write('build {}: cp {}\n'
                        .format(from_node, to_node_list))

    @staticmethod
    def build(temp_dir, nodes, args):
        subprocess.check_call([
            'ninja',
            '-j1',
            '-f',
            NinjaBuilder.__build_ninja_path(temp_dir),
        ] + map(str, nodes), cwd=temp_dir)

    @staticmethod
    def wait_for_stamp_update():
        bss.util.wait_for_temp_file_system_stamp_update()

class TupBuilder(Builder):
    name = 'tup'

    @staticmethod
    def set_up(temp_dir, dag, args):
        tupfile_ini_path \
            = os.path.join(temp_dir, 'Tupfile.ini')
        with open(tupfile_ini_path, 'w') as tupfile_ini:
            pass

        tupfile_path = os.path.join(temp_dir, 'Tupfile')
        with open(tupfile_path, 'w') as tupfile:
            # Tup seems to require rules to be specified in
            # sorted order.  That is, non-leaf nodes need
            # the rule creating the node to preceed rules
            # depending upon the node.
            visited_nodes = set()
            for (from_node, to_nodes) \
                    in reversed(list(dag.flatten())):
                if to_nodes:
                    tupfile.write(
                        ': {} |> cat %f >%o |> {}\n'.format(
                            ' '.join(map(str, to_nodes)),
                            from_node,
                        ),
                    )

    @staticmethod
    def build(temp_dir, nodes, args):
        subprocess.check_call(
            ['tup', '-j1'] + map(str, nodes),
            cwd=temp_dir,
        )

    @staticmethod
    def wait_for_stamp_update():
        bss.util.wait_for_temp_file_system_stamp_update()

all_builders = [
    GNUMakeBuilder,
    NinjaBuilder,
    TupBuilder,
]
