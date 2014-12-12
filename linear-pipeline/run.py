#!/usr/bin/env python2.7

from linearpipeline import LinearPipelineTest
import bsstest
import importlib
import os
import subprocess
import sys
import tempfile

tests = [
    'gnumake',
    'ninja',
]

def main():
    test_classes = []
    for test in tests:
        module = importlib.import_module(test)
        test_classes += module.test_classes

    test_data = []
    for test_class in test_classes:
        for input in test_class.default_inputs():
            instance = test_class(*input)
            time = instance.test()
            test_data.append((instance, time))

    file_name = 'plot.gif'
    bsstest.create_plot(test_data, file_name)
    print('Created {}'.format(file_name))

if __name__ == '__main__':
    main()
