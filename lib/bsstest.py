from lib.gnuplot import layout_for_plot_count
from lib.gnuplot import temp_plot_file
import argparse
import collections
import contextlib
import shutil
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

def main(class_groups):
    parser = arg_parser()
    for classes in class_groups:
        for cls in classes:
            cls._augment_arg_parser(parser)
    args = parser.parse_args()

    with temp_plot_file() as plot_file:
        plot_file.write_gif_header('plot.gif')

        # Shift all the plots up to make room for the
        # legend.
        bottom_offset = 0.030
        scale_factor = 1 - bottom_offset / 2
        plot_file.write_set(
            'multiplot',
            kwoptions=[
                ('layout', layout_for_plot_count(
                    len(class_groups),
                )),
                ('scale', (scale_factor, scale_factor)),
                ('offset', (0, bottom_offset)),
            ]
        )

        first = True
        for classes in class_groups:
            if first:
                # Show the first plot's legend at the
                # bottom.
                plot_file.write_raw(
                    'set key at screen 0.5, screen 0.0 '
                    'center bottom maxrows 1\n'
                )
                first = False

            test_data = list(yield_test_data(classes, args))
            plot_test_data(plot_file, test_data)
            plot_file.write_set('key', False)
        plot_file.write_unset('multiplot')
