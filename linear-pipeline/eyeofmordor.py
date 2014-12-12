#!/usr/bin/env python2.7

import os
import sys
sys.path.append(
    os.path.join( os.path.dirname(__file__), '..', 'lib'),
)

from eyeofmordorbase import EyeOfMordorTestBase
from linearpipelinebase import LinearPipelineTestBase
import bsstest
import shutil

class EyeOfMordorLinearPipelineTest(
    LinearPipelineTestBase,
    EyeOfMordorTestBase,
):
    def _run(self, temp_dir):
        prefix = os.path.join(temp_dir, 'file_')
        for i in xrange(1, self._depth):
            shutil.copy(
                prefix + str(i),
                prefix + str(i + 1),
            )

test_classes = [EyeOfMordorLinearPipelineTest]

def main():
    bsstest.test_and_plot(test_classes)

if __name__ == '__main__':
    main()
