#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for illuminatio.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 3.1.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
import sys

from setuptools import setup

try:
    import setuptools
    if int(setuptools.__version__.split('.')[0]) < 38:
        print("Error: version of setuptools is too old (<38)!")
        sys.exit(1)
except (ImportError, ValueError):
    print("Error: setuptools is not properly installed!")
    sys.exit(1)


if __name__ == "__main__":
    setup(use_pyscaffold=True)
