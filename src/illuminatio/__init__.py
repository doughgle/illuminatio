# -*- coding: utf-8 -*-
"""
Mandatory file for this python module
"""
# Simplified version detection that works with Python 3.12+
try:
    # For installed package
    from importlib.metadata import version as v
    try:
        __version__ = v("illuminatio")
    except Exception:
        __version__ = "unknown"
except ImportError:
    # If import fails, default to unknown
    __version__ = "unknown"
