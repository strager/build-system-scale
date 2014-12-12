import contextlib
import shutil
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
    def test_and_report(self, iterations=5):
        time = self.test()
        sys.stdout.write('{} {} {}\n'.format(
            self._name,
            time,
            ' '.join(map(str, self._inputs)),
        ))

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
