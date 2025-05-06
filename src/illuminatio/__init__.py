# -*- coding: utf-8 -*-
"""
Mandatory file for this python module
"""
try:
    # Python 3.8+
    from importlib.metadata import version, PackageNotFoundError
    try:
        # Change here if project is renamed and does not equal the package name
        __version__ = version(__name__)
    except PackageNotFoundError:
        __version__ = "unknown"
except ImportError:
    # Fallback for older Python versions
    from pkg_resources import get_distribution, DistributionNotFound
    try:
        # Change here if project is renamed and does not equal the package name
        __version__ = get_distribution(__name__).version
    except DistributionNotFound:
        __version__ = "unknown"
