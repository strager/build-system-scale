import contextlib
import math
import subprocess
import tempfile

class PlotFile(object):
    def __init__(self, plot_file):
        self.__file = plot_file

    @staticmethod
    def __sanitize_string(value):
        return str(value)  # TODO(strager)

    @staticmethod
    def sanitize(value):
        if isinstance(value, basestring):
            return '"{}"'.format(
                PlotFile.__sanitize_string(value),
            )
        elif isinstance(value, tuple):
            return ', '.join(map(PlotFile.sanitize, value))
        elif value == float(value) \
                and not isinstance(value, bool):
            return str(float(value))
        else:
            return 'on' if value else 'off'

    @staticmethod
    def gnuplot(plot_file_name):
        subprocess.check_call(['gnuplot', plot_file_name])

    def write_raw(self, string):
        self.__file.write(string)

    def write_set(self, name, value=None, kwoptions=[]):
        self.write_raw('set {}'.format(
            PlotFile.__sanitize_string(name),
        ))
        if value is not None:
            self.write_raw(' {}'.format(
                PlotFile.sanitize(value),
            ))
        for (name, value) in kwoptions:
            self.write_raw(' {} {}'.format(
                PlotFile.__sanitize_string(name),
                PlotFile.sanitize(value),
            ))
        self.write_raw('\n')

    def write_unset(self, name):
        self.write_raw('unset {}'.format(
            PlotFile.__sanitize_string(name),
        ))

    def write_gif_header(self, output_file_name):
        self.write_set('terminal', 'gif')
        self.write_set('output', output_file_name)

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
                self.write_set(name, str(value))
        self.write_raw('plot {}\n'.format(
            ', '.join(
                '"-" title {} with linespoints'.format(
                    PlotFile.sanitize(str(series_name)),
                )
                for series_name in series_points.iterkeys()
            )
        ))
        for points in series_points.itervalues():
            for (x, y) in points:
                self.write_raw(' '.join([
                    PlotFile.sanitize(x),
                    PlotFile.sanitize(y),
                ]) + '\n')
            self.write_raw('e\n')

    def flush(self):
        self.__file.flush()

@contextlib.contextmanager
def temp_plot_file():
    with tempfile.NamedTemporaryFile('w') as temp_file:
        plot_file = PlotFile(temp_file)
        yield plot_file
        plot_file.flush()
        PlotFile.gnuplot(temp_file.name)

def layout_for_plot_count(count):
    # Find a value N which fits all plots in an NxN grid.
    square_root = math.ceil(math.sqrt(count))
    # Prefer stacking graphs vertically.  For example,
    # create a 3-row 2-column grid for 6-count.
    rows = square_root
    columns = math.ceil(float(count) / rows)
    return (int(rows), int(columns))
