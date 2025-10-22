#
# This file is part of pleiades_lpf
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define data model for citations in Pleiades LPF.
"""

from .identifiers import Identifier, URLIdentifier, VALID_IDENTIFIER_TYPES
from .text import normalize_text


class Citation:
    """
    Cites a single addressable component of a bibliographic work or other reference.
    """

    def __init__(
        self,
        id: str,
        short_title: str = "",
        formatted_citation: str = "",
        access_url: str = "",
        bibliographic_url: str = "",
    ):
        self.id = id
        if short_title:
            self.short_title = short_title
        else:
            self._short_title = ""
        if formatted_citation:
            self.formatted_citation = formatted_citation
        else:
            self._formatted_citation = ""
        if access_url:
            self.access_url = access_url
        else:
            self._access_url = ""
        if bibliographic_url:
            self.bibliographic_url = bibliographic_url
        else:
            self._bibliographic_url = ""

    @property
    def id(self) -> str:
        """Get the citation identifier."""
        return str(self._id)

    @id.setter
    def id(self, id: str):
        """Set the citation identifier."""
        self._id = Identifier("alphanumeric", id)

    @property
    def short_title(self) -> str:
        """Get the short title of the cited work."""
        return self._short_title

    @short_title.setter
    def short_title(self, short_title: str):
        """Set the short title of the cited work."""
        short_title = normalize_text(short_title)
        self._short_title = short_title.strip()

    @property
    def formatted_citation(self) -> str:
        """Get the formatted citation string."""
        return self._formatted_citation

    @formatted_citation.setter
    def formatted_citation(self, formatted_citation: str):
        """Set the formatted citation string."""
        formatted_citation = normalize_text(formatted_citation)
        self._formatted_citation = normalize_text(formatted_citation)

    @property
    def access_url(self) -> str:
        """Get the access URL for the cited work."""
        return str(self._access_url)

    @access_url.setter
    def access_url(self, access_url: str):
        """Set the access URL for the cited work."""
        self._access_url = URLIdentifier(access_url)
