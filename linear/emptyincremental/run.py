#!/usr/bin/env python2.7

import os
import sys
sys.path.append(
    os.path.join(os.path.dirname(__file__), '..', '..'),
)

import importlib
import lib.bsstest

tests = [
    'linear.emptyincremental.eyeofmordor',
    'linear.emptyincremental.gnumake',
    'linear.emptyincremental.ninja',
]

test_classes = []
for test in tests:
    module = importlib.import_module(test)
    test_classes += module.test_classes

def main():
    lib.bsstest.sub_main(test_classes)

if __name__ == '__main__':
    main()
