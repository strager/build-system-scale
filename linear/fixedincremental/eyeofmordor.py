#!/usr/bin/env python2.7

import os
import sys
sys.path.append(
    os.path.join(os.path.dirname(__file__), '..', '..'),
)

from linear.eyeofmordorbase import EyeOfMordorLinearTestBase
from linear.fixedincremental.fixedincrementalbase \
    import FixedIncrementalTestBase
import lib.bsstest

class Test(
    FixedIncrementalTestBase,
    EyeOfMordorLinearTestBase,
):
    def _run(self, temp_dir):
        self._build(
            temp_dir,
            start=self._depth - self._incremental_depth,
        )

test_classes = [Test]

def main():
    lib.bsstest.test_and_plot(test_classes)

if __name__ == '__main__':
    main()
