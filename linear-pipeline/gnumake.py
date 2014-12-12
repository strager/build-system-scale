#!/usr/bin/env python2.7

from bsstest import BSSTest
import os
import subprocess
import sys

class GNUMakeTest(BSSTest):
    def __init__(self, depth):
        self.__depth = depth

    @property
    def _name(self):
        return 'gnumake'

    @property
    def _inputs(self):
        return (self.__depth,)

    def _set_up(self, temp_dir):
        makefile_path = os.path.join(
            temp_dir, 'GNUMakefile')
        with open(makefile_path, 'w') as makefile:
            for i in xrange(1, self.__depth):
                makefile.write(
                   'file_{}: file_{}\n\t@cp $< $@\n'.format(
                        i + 1,
                    i,
                    ),
                )
        f_path = os.path.join( temp_dir, 'file_1')
        with open(f_path, 'wb') as f:
            f.write('hello world')

    def _run(self, temp_dir):
        subprocess.check_call([
            'make',
            '-f',
            'GNUMakefile',
            'file_{}'.format(self.__depth),
        ], cwd=temp_dir)

def main():
    for depth in map(int, sys.argv[1:]):
        GNUMakeTest(depth=depth).test_and_report()

if __name__ == '__main__':
    main()
