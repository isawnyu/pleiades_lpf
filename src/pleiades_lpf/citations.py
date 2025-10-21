#
# This file is part of pleiades_lpf
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define data model for citations in Pleiades LPF.
"""


class Citation:
    """
    Cites a single addressable component of a bibliographic work or other reference.
    """

    def __init__(self, source: str, page: str | None = None, note: str | None = None):
        self.id`: `Identifier`
        self.short_title`: `str`
        self.formatted_citation`: `str`
        self.access_url`: `url`
        self.bibliographic_url`: `url`


class CitedWork:
    """
    A work that can be cited in the gazetteer.
    """

    def __init__(self, title: str, author: str | None = None, year: int | None = None):
        self.title = title  # Title of the work
        self.author = author  # Optional author of the work
        self.year = year  # Optional publication year
