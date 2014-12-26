import bss.gnuplot
import bss.util
import collections
import contextlib
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
import xml.sax.saxutils

def e(string):
    '''
    Escapes a string so it may be embedded in HTML as
    content or part of a quoted attribute.
    '''
    return xml.sax.saxutils.escape(str(string))

def title(args, dag_set, setup):
    return '{}, {}'.format(
        setup.name(args),
        dag_set.name,
    )
_y_label = 'Time (seconds)'

def make_run_plot_datas(runs):
    '''
    Turns a list of Runs into nested dicts:

    (dag_set, setup) => builder => runs
    '''
    datas = collections.defaultdict(
        lambda: collections.defaultdict(list))
    for run in runs:
        datas[(run.dag_set, run.setup)][run.builder] \
            .append(run)
    return datas

def multiplot(run_plot_datas, plot_file, args):
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
                    len(run_plot_datas),
                ),
            ),
            ('scale', (scale_factor, scale_factor)),
            ('offset', (0, bottom_offset)),
        ]
    )

    first = True
    for ((dag_set, setup), builder_runs) \
            in run_plot_datas.iteritems():
        if first:
            # Show the first plot's legend at the
            # bottom.
            plot_file.write_raw(
                'set key at screen 0.5, screen 0.0 '
                'center bottom maxrows 1\n'
            )
            first = False

        plot_file.write_plot(
            title=title(
                args=args,
                dag_set=dag_set,
                setup=setup,
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
                in builder_runs.iteritems()
            },
        )
        plot_file.write_set('key', False)
    plot_file.write_unset('multiplot')

@contextlib.contextmanager
def html_plot_file(html_file, encoding='utf-8'):
    with tempfile.NamedTemporaryFile() as svg_file:
        with bss.gnuplot.temp_plot_file() as plot_file:
            plot_file.write_svg_header(svg_file.name)
            yield plot_file

        # Sorry for touching global state.  ElementTree made
        # me do it.
        ET.register_namespace(
            '',
            'http://www.w3.org/2000/svg',
        )
        ET.register_namespace(
            'xlink',
            'http://www.w3.org/1999/xlink',
        )

        svg_file.seek(0)
        svg_tree = ET.parse(svg_file)
        svg_tree.write(
            html_file,
            encoding=encoding,
            method='html',
            xml_declaration=False,
        )
        html_file.write('\n')

def write_system_information_html(builders, html_file):
    (
        uname_sysname,
        _uname_nodename,
        uname_release,
        uname_version,
        _uname_machine,
    ) = os.uname()
    processors = bss.util.processors_info()
    html_file.write('''<h2>System information</h2>
<dl>
    <dt>Invocation (<code>sys.argv</code>)
    <dd><pre>{argv}</pre>
    <dt>Operating system (<code>uname -srv</code>)
    <dd>{uname_sysname} {uname_release} {uname_version}
    <dt>Processors
    <dd>{processors}
'''.format(
    argv=e(repr(sys.argv)),
    processors=(
        '\n    <dd>'.join(map(e, processors))
        if processors
        else '(unavailable)'
    ),
    uname_release=e(uname_release),
    uname_sysname=e(uname_sysname),
    uname_version=e(uname_version),
))

    for builder in sorted(
        builders,
        key=lambda builder: builder.name,
    ):
        html_file.write('''
    <dt>Version of {builder}
    <dd><pre>{version}</pre>
'''.format(
    builder=e(builder.name),
    version=e(builder.version()),
))

    html_file.write('</dl>\n')

def write_report(runs, args):
    all_runs = list(runs)
    encoding = 'utf-8'
    with file(args.output_html_path, 'w') as html_file:
        html_file.write('''<!DOCTYPE html>
<html lang=en>
<head>
<meta charset='{encoding}'>
<title>BSS report</title>
<style>
body {{
    font-family: sans-serif;
}}
tbody > tr > th {{
    text-align: inherit;
}}
caption {{
    font-weight: bold;
}}
</style>
</head>
<body>
<h1>BSS report</h1>
<p>Here's an awesome graph:
<div class=graph>
'''.format(encoding=e(encoding)))

        run_plot_datas = make_run_plot_datas(all_runs)
        with html_plot_file(html_file, encoding='utf-8') \
                as plot_file:
            multiplot(
                args=args,
                plot_file=plot_file,
                run_plot_datas=run_plot_datas,
            )

        for ((dag_set, setup), builder_runs) \
                in run_plot_datas.iteritems():
            # builder => variable => runs
            builder_variable_runs = collections.defaultdict(
                lambda: collections.defaultdict(list))
            for (builder, runs) in builder_runs.iteritems():
                for run in runs:
                    builder_variable_runs[builder] \
                        [run.variable].append(run)

            max_measurements = max(
                len(variable_runs.values())
                for variable_runs
                in builder_variable_runs.itervalues()
            )
            html_file.write('''<table>
<caption>{title}</caption>
<thead>
<tr>
    <th>Build System</th>
    <th>{variable}</th>
    <th colspan='{time_colspan}'>Time (seconds)</th>
</tr>
</thead>
<tbody>
'''.format(
    time_colspan=e(max_measurements),
    title=title(args=args, dag_set=dag_set, setup=setup),
    variable=e(dag_set.variable_label),
))
            for (builder, variable_runs) \
                    in builder_variable_runs.iteritems():
                first = True
                for (variable, runs) \
                        in variable_runs.iteritems():
                    html_file.write('<tr>\n')
                    if first:
                        html_file.write('''\
    <th rowspan={rowspan}>{builder}</th>
'''.format(
    builder=e(builder.name),
    rowspan=e(len(variable_runs))),
)
                        first = False
                    html_file.write('    <td>{}</td>\n'
                        .format(e(variable)))
                    for run in runs:
                        html_file.write('    <td>{}</td>\n'
                            .format(e(run.measurement)))
                    html_file.write('</tr>\n')
            html_file.write('</tbody>\n</table>\n')

        write_system_information_html(
            builders={run.builder for run in all_runs},
            html_file=html_file,
        )

        html_file.write('''</div>
</body>
</html>
''')
