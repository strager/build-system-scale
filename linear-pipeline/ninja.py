#!/usr/bin/env python2.7

import os
import sys
sys.path.append(
    os.path.join( os.path.dirname(__file__), '..', 'lib'),
)

from linearpipeline import LinearPipelineTest
import bsstest
import subprocess

class NinjaTest(LinearPipelineTest):
    name = 'ninja'

    def _set_up(self, temp_dir):
        super(NinjaTest, self)._set_up(temp_dir)
        ninja_path = os.path.join(temp_dir, 'build.ninja')
        with open(ninja_path, 'w') as ninja:
            ninja.write('ninja_required_version = 1.0\n')
            ninja.write('rule cp\n command = cp $in $out\n')
            for i in xrange(1, self._depth):
                ninja.write(
                   'build file_{}: cp file_{}\n'.format(
                        i + 1,
                        i,
                    ),
                )

    def _run(self, temp_dir):
        subprocess.check_call([
            'ninja',
            '-f',
            'build.ninja',
            'file_{}'.format(self._depth),
        ], cwd=temp_dir)

test_classes = [NinjaTest]

def main():
    bsstest.test_and_plot(test_classes)

if __name__ == '__main__':
    main()
