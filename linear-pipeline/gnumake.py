#!/usr/bin/env python2.7

from linearpipeline import LinearPipelineTest
import os
import subprocess
import sys

class GNUMakeTest(LinearPipelineTest):
    name = 'gnumake'

    def _set_up(self, temp_dir):
        super(GNUMakeTest, self)._set_up(temp_dir)
        makefile_path = os.path.join(
            temp_dir,
            'GNUMakefile',
        )
        with open(makefile_path, 'w') as makefile:
            for i in xrange(1, self._depth):
                makefile.write(
                   'file_{}: file_{}\n\t@cp $< $@\n'.format(
                        i + 1,
                        i,
                    ),
                )

    def _run(self, temp_dir):
        subprocess.check_call([
            'make',
            '-f',
            'GNUMakefile',
            'file_{}'.format(self._depth),
        ], cwd=temp_dir)

test_classes = [GNUMakeTest]

def main():
    LinearPipelineTest.write_report_header(sys.stdout)
    for test_class in test_classes:
        test_class.create_test_and_report(
            data_file=sys.stdout,
        )

if __name__ == '__main__':
    main()
