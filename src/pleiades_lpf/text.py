#
# This file is part of pleiades_lpf
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Text handling utilities for Pleiades LPF."""

from textnorm import normalize_space, normalize_unicode


def normalize_text(text: str) -> str:
    """Normalize text by applying Unicode normalization and whitespace normalization."""
    text = normalize_unicode(text)
    text = normalize_space(text)
    return text
