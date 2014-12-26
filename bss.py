#!/usr/bin/env python2.7

import argparse
import bss.builders
import bss.dagsets
import bss.gnuplot
import bss.run
import bss.setups
import bss.util
import collections

def plot(runs, args):
    # (dag_set, setup) => builder => runs
    grouped = collections.defaultdict(
        lambda: collections.defaultdict(list))
    for run in runs:
        grouped[(run.dag_set, run.setup)][run.builder] \
            .append(run)

    with bss.gnuplot.temp_plot_file() as plot_file:
        plot_file.write_gif_header('plot.gif')

        # Shift all the plots up to make room for the
        # legend.
        bottom_offset = 0.030
        scale_factor = 1 - bottom_offset / 2
        plot_file.write_set(
            'multiplot',
            kwoptions=[
                (
                    'layout',
                    bss.gnuplot.layout_for_plot_count(
                        len(grouped),
                    ),
                ),
                ('scale', (scale_factor, scale_factor)),
                ('offset', (0, bottom_offset)),
            ]
        )

        first = True
        for ((dag_set, setup), config_runs) \
                in grouped.iteritems():
            if first:
                # Show the first plot's legend at the
                # bottom.
                plot_file.write_raw(
                    'set key at screen 0.5, screen 0.0 '
                    'center bottom maxrows 1\n'
                )
                first = False

            plot_file.write_plot(
                title='{}, {}'.format(
                    setup.name(args),
                    dag_set.name,
                ),
                x_label=dag_set.variable_label,
                y_label='Time (seconds)',
                series_points={
                    builder.name: [
                        (
                            run.variable,
                            run.measurement,
                        )
                        for run in runs
                    ]
                    for (builder, runs)
                    in config_runs.iteritems()
                },
            )
            plot_file.write_set('key', False)
        plot_file.write_unset('multiplot')

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
    plot(args=args, runs=runs)

if __name__ == '__main__':
    main()
