#!/usr/bin/env python2.7

import os
import sys
sys.path.append(
    os.path.join(os.path.dirname(__file__), '..', '..'),
)

from lib.gnumakebase import GNUMakeTestBase
from linear.linearbase import LinearTestBase
import lib.bsstest

class GNUMakeLinearTest(LinearTestBase, GNUMakeTestBase):
    def _set_up(self, temp_dir):
        super(GNUMakeLinearTest, self) \
            ._set_up(temp_dir)
        makefile_path = self._makefile_path(temp_dir)
        with open(makefile_path, 'w') as makefile:
            for i in xrange(self._depth - 1, 0, -1):
                makefile.write(
                   'file_{}: file_{}\n\t@cp $< $@\n'.format(
                        i + 1,
                        i,
                    ),
                )

test_classes = [GNUMakeLinearTest]

def main():
    lib.bsstest.test_and_plot(test_classes)

if __name__ == '__main__':
    main()
