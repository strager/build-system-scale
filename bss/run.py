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

def measure_configuration(
    args,
    builder,
    dag,
    setup,
    iterations=1,
):
    measurements = []
    build_nodes = dag.root_nodes()
    for _ in xrange(iterations):
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
            measurements.append(end - start)
    return measurements

def run_configurations(
    args,
    builders,
    dag_sets,
    setups,
):
    if args.iterations < 0:
        raise Exception('--iterations must be non-negative')
    if args.warmup_iterations < 0:
        raise Exception(
            '--warmup-iterations must be non-native',
        )
    for builder in builders:
        for dag_set in dag_sets:
            for setup in setups:
                dags = dag_set.dags(args)
                for (variable, dag) in dags:
                    measurements = measure_configuration(
                        args=args,
                        builder=builder,
                        dag=dag,
                        setup=setup,
                        iterations=args.iterations
                            + args.warmup_iterations,
                    )
                    good_measurements = measurements[
                        args.warmup_iterations:
                    ]
                    for measurement in good_measurements:
                        yield Run(
                            builder=builder,
                            dag=dag,
                            dag_set=dag_set,
                            measurement=measurement,
                            setup=setup,
                            variable=variable,
                        )
