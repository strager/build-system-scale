#!/usr/bin/env python2.7

import argparse
import bss.builders
import bss.dagsets
import bss.gnuplot
import bss.setups
import bss.util
import collections

Run = collections.namedtuple('Run', [
    'builder',
    'dag',
    'dag_set',
    'measurement',
    'setup',
    'variable',
])

def run_configuration_once(args, builder, dag, setup):
    build_nodes = dag.root_nodes()
    with bss.util.temporary_directory() as temp_dir:
        builder.set_up(
            args=args,
            dag=dag,
            temp_dir=temp_dir,
        )
        setup.set_up(
            args=args,
            build_nodes=build_nodes,
            builder=builder,
            dag=dag,
            temp_dir=temp_dir,
        )
        start = bss.util.get_time()
        builder.build(
            args=args,
            nodes=build_nodes,
            temp_dir=temp_dir,
        )
        end = bss.util.get_time()
        return end - start

def run_configuration(args, builder, dag, setup):
    measurements = [run_configuration_once(
        args=args,
        builder=builder,
        dag=dag,
        setup=setup,
    ) for _ in xrange(args.iterations)]
    return min(measurements)

def run_configuration_set(args, builder, dag_set, setup):
    dags = dag_set.dags(args)
    for (variable, dag) in dags:
        measurement = run_configuration(
            args=args,
            builder=builder,
            dag=dag,
            setup=setup,
        )
        yield Run(
            builder=builder,
            dag=dag,
            dag_set=dag_set,
            measurement=measurement,
            setup=setup,
            variable=variable,
        )

def run_configuration_sets(
    args,
    builders,
    dag_sets,
    setups,
):
    for builder in builders:
        for dag_set in dag_sets:
            for setup in setups:
                for run in run_configuration_set(
                    args=args,
                    builder=builder,
                    dag_set=dag_set,
                    setup=setup,
                ):
                    yield run

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
    for builder in builders:
        builder.prepare_parser(parser)
    for dag_set in dag_sets:
        dag_set.prepare_parser(parser)
    for setup in setups:
        setup.prepare_parser(parser)

def main():
    builders = bss.builders.all_builders
    dag_sets = bss.dagsets.all_dag_sets
    setups = bss.setups.all_setups

    parser = argparse.ArgumentParser()
    prepare_parser(
        parser,
        builders=builders,
        dag_sets=dag_sets,
        setups=setups,
    )
    args = parser.parse_args()

    runs = list(run_configuration_sets(
        args=args,
        builders=builders,
        dag_sets=dag_sets,
        setups=setups,
    ))
    plot(args=args, runs=runs)

if __name__ == '__main__':
    main()
