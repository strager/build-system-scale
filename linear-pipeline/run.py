#!/usr/bin/env python2.7

import bsstest
import importlib

tests = [
    'gnumake',
    'ninja',
]

def main():
    test_classes = []
    for test in tests:
        module = importlib.import_module(test)
        test_classes += module.test_classes
    bsstest.test_and_plot(test_classes)

if __name__ == '__main__':
    main()
