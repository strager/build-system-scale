#!/usr/bin/env python2.7

import os
import sys
sys.path.append(
    os.path.join(os.path.dirname(__file__), '..', '..'),
)

from lib.eyeofmordorbase import EyeOfMordorTestBase
from linear.linearbase import LinearTestBase
import lib.bsstest
import shutil

class EyeOfMordorLinearTest(
    LinearTestBase,
    EyeOfMordorTestBase,
):
    def _run(self, temp_dir):
        prefix = os.path.join(temp_dir, 'file_')
        for i in xrange(1, self._depth):
            shutil.copy(
                prefix + str(i),
                prefix + str(i + 1),
            )

test_classes = [EyeOfMordorLinearTest]

def main():
    lib.bsstest.test_and_plot(test_classes)

if __name__ == '__main__':
    main()
