#!/usr/bin/env python2.7

import os
import sys
sys.path.append(
    os.path.join(os.path.dirname(__file__), '..', '..'),
)

from linear.fullincremental.fullincrementalbase \
    import FullIncrementalTestBase
from linear.gnumakebase import GNUMakeLinearTestBase
import lib.bsstest

class Test(
    GNUMakeLinearTestBase,
    FullIncrementalTestBase,
):
    pass

test_classes = [Test]

def main():
    lib.bsstest.test_and_plot(test_classes)

if __name__ == '__main__':
    main()