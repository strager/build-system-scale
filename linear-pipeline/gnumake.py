#!/usr/bin/env python2.7

import os
import sys
sys.path.append(
    os.path.join( os.path.dirname(__file__), '..', 'lib'),
)

from gnumakebase import GNUMakeTestBase
from linearpipeline import LinearPipelineTest
import bsstest

class GNUMakeLinearPipelineTest(
    LinearPipelineTest,
    GNUMakeTestBase,
):
    def _set_up(self, temp_dir):
        super(GNUMakeLinearPipelineTest, self) \
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

test_classes = [GNUMakeLinearPipelineTest]

def main():
    bsstest.test_and_plot(test_classes)

if __name__ == '__main__':
    main()
