import argparse
import collections
import contextlib
import math
import shutil
import subprocess
import sys
import tempfile
import time
import timeit

get_time = timeit.default_timer

def temp_file_system_stamp_resolution():
    resolutions = []
    if sys.platform == 'darwin':
        # HGFS+ mtime resolution.
        resolutions.append(1)
    if sys.platform not in ('cygwin', 'darwin', 'win32'):
        # ext3 mtime resolution.
        resolutions.append(1)
        # ext4 mtime resolution.
        resolutions.append(10 ** -9)
    if sys.platform in ('cygwin', 'win32'):
        # FAT32 mtime resolution.
        resolutions.append(2)
        # NTFS mtime resolution.
        resolutions.append(100 * (10 ** -9))
    # System clock resolution.
    resolutions.append(0.02)
    return max(resolutions)

@contextlib.contextmanager
def temporary_directory():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

class BSSTest(object):
    def test(self, iterations=5):
        times \
            = [self.test_once() for _ in xrange(iterations)]
        return min(times)

    def test_once(self):
        with temporary_directory() as temp_dir:
            self._set_up(temp_dir)
            start = get_time()
            self._run(temp_dir)
            end = get_time()
            return end - start

    @classmethod
    def _augment_arg_parser(cls, arg_parser):
        pass

    def _set_up(self, temp_dir):
        pass

    def _wait_for_stamp_update(self):
        time.sleep(temp_file_system_stamp_resolution())

class PlotFile(object):
    def __init__(self, plot_file):
        self.__file = plot_file

    @staticmethod
    def sanitize(string):
        return string  # TODO(strager)

    @staticmethod
    def gnuplot(plot_file_name):
        subprocess.check_call(['gnuplot', plot_file_name])

    def begin_multiplot(self, layout=None):
        self.__file.write('set multiplot')
        if layout is not None:
            self.__file.write(' layout {},{}'.format(
                PlotFile.sanitize(int(layout[0])),
                PlotFile.sanitize(int(layout[1])),
            ))
        self.__file.write('\n')

    def end_multiplot(self):
        self.__file.write('unset multiplot\n')

    def write_gif_header(self, output_file_name):
        self.__file.write('set terminal gif\n')
        self.__file.write('set output "{}"\n'.format(
            PlotFile.sanitize(output_file_name),
        ))

    def write_plot(
        self,
        series_points,  # {'series', [(x, y), ...]), ...}
        title=None,
        x_label=None,
        y_label=None,
    ):
        options = {
            'title': title,
            'xlabel': x_label,
            'ylabel': y_label,
        }
        for (name, value) in options.iteritems():
            if value is not None:
                self.__file.write('set {} "{}"\n'.format(
                    PlotFile.sanitize(name),
                    PlotFile.sanitize(value),
                ))
        self.__file.write('plot {}\n'.format(
            ', '.join(
                '"-" title "{}" with linespoints'
                    .format(PlotFile.sanitize(series_name))
                for series_name in series_points.iterkeys()
            )
        ))
        for points in series_points.itervalues():
            for (x, y) in points:
                self.__file.write(' '.join([
                    PlotFile.sanitize(str(x)),
                    PlotFile.sanitize(str(y)),
                ]) + '\n')
            self.__file.write('e\n')

    def flush(self):
        self.__file.flush()

@contextlib.contextmanager
def temp_plot_file():
    with tempfile.NamedTemporaryFile('w') as temp_file:
        plot_file = PlotFile(temp_file)
        yield plot_file
        plot_file.flush()
        PlotFile.gnuplot(temp_file.name)

def plot_test_data(plot_file, data, title=None):
    """
    data is [
        (BSSTest instance, time),
        (BSSTest instance, time),
        ...
    ]
    """
    data_by_class = collections.defaultdict(list)
    for pair in data:
        data_by_class[pair[0].__class__].append(pair)
    if not data_by_class:
        # No data to plot.
        plot_file.write_plot({})
        return
    first_class = next(data_by_class.iterkeys())
    plot_file.write_plot(
        title=first_class.title,
        x_label=first_class.fields[0],
        y_label='Time (seconds)',
        series_points={
            cls.name: [
                (instance.inputs[0], time)
                for (instance, time) in data
            ]
            for (cls, data) in data_by_class.iteritems()
        },
    )

def yield_test_data(classes, args):
    test_data = []
    for cls in classes:
        for input in cls.default_inputs(args):
            instance = cls(*input)
            time = instance.test()
            yield (instance, time)

def arg_parser():
    arg_parser = argparse.ArgumentParser()
    def has_action(name):
        return any(
            action.dest == name
            for action in arg_parser._actions
        )
    setattr(arg_parser, 'has_action', has_action)
    return arg_parser

def sub_main(classes):
    parser = arg_parser()
    for cls in classes:
        cls._augment_arg_parser(parser)
    args = parser.parse_args()
    test_data = list(yield_test_data(classes, args))
    with temp_plot_file() as plot_file:
        plot_file.write_gif_header('plot.gif')
        plot_test_data(plot_file, test_data)

def layout_for_plot_count(count):
    # Find a value N which fits all plots in an NxN grid.
    square_root = math.ceil(math.sqrt(count))
    # Prefer stacking graphs vertically.  For example,
    # create a 3-row 2-column grid for 6-count.
    rows = square_root
    columns = math.ceil(float(count) / rows)
    return (int(rows), int(columns))

def main(class_groups):
    parser = arg_parser()
    for classes in class_groups:
        for cls in classes:
            cls._augment_arg_parser(parser)
    args = parser.parse_args()
    with temp_plot_file() as plot_file:
        plot_file.write_gif_header('plot.gif')
        plot_file.begin_multiplot(
            layout=layout_for_plot_count(len(class_groups)),
        )
        for classes in class_groups:
            test_data = list(yield_test_data(classes, args))
            plot_test_data(plot_file, test_data)
        plot_file.end_multiplot()
