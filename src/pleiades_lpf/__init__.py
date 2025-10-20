#
# This file is part of pleiades_lpf
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Tools for reading and writing Linked Places Format (LPF) JSON files.
LPF is a JSON-based format for encoding information about places and their
relationships. It is defined by https://github.com/LinkedPasts/linked-places-format

This package provides functions to serialize and deserialize LPF data.
"""
__version__ = "0.0.1"
__all__ = [
    "dump",
    "dumps",
    "load",
    "loads",
]
__author__ = "Tom Elliott <tom.elliott@nyu.edu>"

import json


def dump(obj, fp, **kwargs):
    """Serialize LPF object to a file-like object as JSON."""
    return json.dump(obj, fp, **kwargs)


def dumps(obj, **kwargs):
    """Serialize LPF object to a JSON string."""
    return json.dumps(obj, **kwargs)


def load(fp, **kwargs):
    """Deserialize LPF object from a file-like object containing JSON."""
    return json.load(fp, **kwargs)


def loads(s, **kwargs):
    """Deserialize LPF object from a JSON string."""
    return json.loads(s, **kwargs)
