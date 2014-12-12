#!/usr/bin/env python2.7

import os
import sys
sys.path.append(
    os.path.join( os.path.dirname(__file__), '..', 'lib'),
)

from ninjabase import NinjaTestBase
from linearpipeline import LinearPipelineTest
import bsstest

class NinjaLinearPipelineTest(
    LinearPipelineTest,
    NinjaTestBase,
):
    def _set_up(self, temp_dir):
        super(NinjaLinearPipelineTest, self) \
            ._set_up(temp_dir)
        build_ninja_path = self._build_ninja_path(temp_dir)
        with open(build_ninja_path, 'w') as ninja:
            ninja.write('ninja_required_version = 1.0\n')
            ninja.write('rule cp\n command = cp $in $out\n')
            for i in xrange(self._depth - 1, 0, -1):
                ninja.write(
                   'build file_{}: cp file_{}\n'.format(
                        i + 1,
                        i,
                    ),
                )
            ninja.write('default file_{}\n'.format(
                self._depth,
            ))

test_classes = [NinjaLinearPipelineTest]

def main():
    bsstest.test_and_plot(test_classes)

if __name__ == '__main__':
    main()
