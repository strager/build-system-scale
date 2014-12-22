#!/usr/bin/env python2.7

import os
import sys
sys.path.append(
    os.path.join(os.path.dirname(__file__), '..', '..'),
)

from linear.eyeofmordorbase import EyeOfMordorLinearTestBase
from linear.emptyincremental.emptyincrementalbase \
    import EmptyIncrementalTestBase
import lib.bsstest

class Test(
    EmptyIncrementalTestBase,
    EyeOfMordorLinearTestBase,
):
    def _run(self, temp_dir):
        pass

test_classes = [Test]

def main():
    lib.bsstest.sub_main(test_classes)

if __name__ == '__main__':
    main()
