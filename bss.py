#!/usr/bin/env python2.7

import argparse
import bss.builders
import bss.dagsets
import bss.gnuplot
import bss.report
import bss.run
import bss.setups
import bss.util

def prepare_parser(parser, builders, dag_sets, setups):
    parser.add_argument(
        '--iterations',
        default=1,
        dest='iterations',
        help='Number of times to run each test',
        metavar='COUNT',
        type=int,
    )
    parser.add_argument(
        '--warmup-iterations',
        default=0,
        dest='warmup_iterations',
        help='Number of runs before measuring',
        metavar='COUNT',
        type=int,
    )
    parser.add_argument(
        '--output-html',
        default='bss.html',
        dest='output_html_path',
        help='Path to the output HTML file',
        metavar='FILE',
        type=str,
    )
    for builder in builders:
        builder.prepare_parser(parser)
    for dag_set in dag_sets:
        dag_set.prepare_parser(parser)
    for setup in setups:
        setup.prepare_parser(parser)

def prepare_enabled_parser(
    parser,
    builders,
    dag_sets,
    setups,
):
    def add_shortname_list_argument(
        name,
        values,
        *kargs,
        **kwargs
    ):
        shortname_to_value \
            = {value.shortname: value for value in values}
        class FromShortnameAction(argparse.Action):
            def __call__(
                self,
                parser,
                namespace,
                values,
                option_string=None,
            ):
                setattr(
                    namespace,
                    self.dest,
                    [
                        shortname_to_value[shortname]
                        for shortname in values
                    ],
                )
        parser.add_argument(
            name,
            action=FromShortnameAction,
            choices=shortname_to_value.keys(),
            default=values,
            nargs='+',
            required=False,
            type=str,
            *kargs,
            **kwargs
        )

    add_shortname_list_argument(
        '--builders',
        builders,
        dest='builders',
        help='Build systems to test',
        metavar='BUILDER',
    )
    add_shortname_list_argument(
        '--dags',
        dag_sets,
        dest='dag_sets',
        help='Graphs to test with',
        metavar='DAG',
    )
    add_shortname_list_argument(
        '--scenarios',
        setups,
        dest='setups',
        help='Test cases to run',
        metavar='SCENARIO',
    )

def main():
    builders = bss.builders.all_builders
    dag_sets = bss.dagsets.all_dag_sets
    setups = bss.setups.all_setups

    # Figure out the list of Builders, DAGSets, and Setups
    # the user cares about.
    parser = argparse.ArgumentParser(add_help=False)
    prepare_enabled_parser(
        parser,
        builders=builders,
        dag_sets=dag_sets,
        setups=setups,
    )
    (args, _) = parser.parse_known_args()
    builders = args.builders
    dag_sets = args.dag_sets
    setups = args.setups

    # Parse options only for the requested Builders,
    # DAGSets, and Setups.
    parser = argparse.ArgumentParser()
    prepare_enabled_parser(
        parser,
        builders=builders,
        dag_sets=dag_sets,
        setups=setups,
    )
    prepare_parser(
        parser,
        builders=builders,
        dag_sets=dag_sets,
        setups=setups,
    )
    args = parser.parse_args()
    builders = args.builders
    dag_sets = args.dag_sets
    setups = args.setups

    runs = list(bss.run.run_configurations(
        args=args,
        builders=builders,
        dag_sets=dag_sets,
        setups=setups,
    ))
    bss.report.write_report(args=args, runs=runs)

if __name__ == '__main__':
    main()
