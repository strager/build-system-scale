#!/usr/bin/env python2.7

import os
import sys
sys.path.append(
    os.path.join(os.path.dirname(__file__), '..', '..'),
)

from linear.fixedincremental.fixedincrementalbase \
    import FixedIncrementalTestBase
from linear.ninjabase import NinjaLinearTestBase
import lib.bsstest

class Test(
    FixedIncrementalTestBase,
    NinjaLinearTestBase,
):
    pass

test_classes = [Test]

def main():
    lib.bsstest.sub_main(test_classes)

if __name__ == '__main__':
    main()
