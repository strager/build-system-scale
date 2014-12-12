#!/usr/bin/env python2.7

import os
import subprocess
import sys

tests = [
    'gnumake.py',
]

def main():
    for test in tests:
        sys.stderr.write('Running {}\n'.format(test))
        subprocess.check_call([
            sys.executable,
            os.path.join(os.path.dirname(__file__), test),
        ] + sys.argv[1:])

if __name__ == '__main__':
    main()
