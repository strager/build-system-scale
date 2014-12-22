#!/usr/bin/env python2.7

import os
import sys
sys.path.append(
    os.path.join(os.path.dirname(__file__), '..'),
)

import importlib
import lib.bsstest

tests = [
    'linear.clean.run',
    'linear.emptyincremental.run',
    'linear.fixedincremental.run',
    'linear.fullincremental.run',
]

test_class_groups = []
for test in tests:
    module = importlib.import_module(test)
    test_class_groups.append(module.test_classes)

def main():
    lib.bsstest.main(test_class_groups)

if __name__ == '__main__':
    main()
