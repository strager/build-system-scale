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

def measure_configuration(args, builder, dag, setup):
    measurements = []
    build_nodes = dag.root_nodes()
    for _ in xrange(args.iterations):
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
    return min(measurements)

def run_configurations(
    args,
    builders,
    dag_sets,
    setups,
):
    for builder in builders:
        for dag_set in dag_sets:
            for setup in setups:
                dags = dag_set.dags(args)
                for (variable, dag) in dags:
                    measurement = measure_configuration(
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
