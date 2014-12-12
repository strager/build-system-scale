import collections
import contextlib
import shutil
import subprocess
import sys
import tempfile
import timeit

get_time = timeit.default_timer

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

def _sanitize_gnuplot_string(string):
    return string  # TODO(strager)

def create_plot(data, file_name):
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

    with tempfile.NamedTemporaryFile('w') as plot_file:
        plot_file.write('set terminal gif\n')
        plot_file.write('set output "{}"\n'.format(
            _sanitize_gnuplot_string(file_name),
        ))
        plot_file.write('set xlabel "{}"\n'.format(
            _sanitize_gnuplot_string(
                next(data_by_class.iterkeys()).fields[0],
            )
        ))
        plot_file.write('set ylabel "Time (seconds)"\n')

        plot_file.write('plot {}\n'.format(
            ', '.join(
                '"-" title "{}" with linespoints'
                    .format(cls.name)
                for cls in data_by_class.iterkeys()
            )
        ))
        for (cls, data) in data_by_class.iteritems():
            for (instance, time) in data:
                plot_file.write(' '.join([
                    str(instance.inputs[0]),
                    str(time),
                ]) + '\n')
            plot_file.write('e\n')

        plot_file.flush()
        subprocess.check_call(['gnuplot', plot_file.name])
