#!/usr/bin/env python2.7

import os
import sys
sys.path.append(
    os.path.join(os.path.dirname(__file__), '..', '..'),
)

from linear.eyeofmordorbase import EyeOfMordorLinearTestBase
from linear.fullincremental.fullincrementalbase \
    import FullIncrementalTestBase
import lib.bsstest

class Test(
    FullIncrementalTestBase,
    EyeOfMordorLinearTestBase,
):
    def _run(self, temp_dir):
        self._build(temp_dir, start=1)

test_classes = [Test]

def main():
    lib.bsstest.sub_main(test_classes)

if __name__ == '__main__':
    main()
