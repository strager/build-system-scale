#!/usr/bin/env python2.7

import os
import sys
sys.path.append(
    os.path.join( os.path.dirname(__file__), '..', '..'),
)

import importlib
import lib.bsstest

tests = [
    'eyeofmordor',
    'gnumake',
    'ninja',
]

def main():
    test_classes = []
    for test in tests:
        module = importlib.import_module(test)
        test_classes += module.test_classes
    lib.bsstest.test_and_plot(test_classes)

if __name__ == '__main__':
    main()
