#
# This file is part of pleiades_lpf
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define data model for citations in Pleiades LPF.
"""

from .identifiers import (
    Identifier,
    URLIdentifier,
    VALID_IDENTIFIER_TYPES,
    make_identifier,
)
from .text import normalize_text
from urllib.parse import urlparse

CITATION_TYPES = {
    "dataSource": "http://purl.org/spar/cito/citesAsDataSource",
    "evidence": "http://purl.org/spar/cito/citesAsEvidence",
    "related": "http://purl.org/spar/cito/citesAsRelated",
    "cites": "http://purl.org/spar/cito/cites",
    "closeMatch": "http://www.w3.org/2008/05/skos-xl#closeMatch",
}
BIBLIOGRAPHIC_URL_NETLOCS = {"www.zotero.org", "search.worldcat.org"}


class Citation:
    """
    Cites a single addressable component of a bibliographic work or other reference.
    """

    def __init__(
        self,
        id: Identifier | str,
        short_title: str = "",
        formatted_citation: str = "",
        access_url: str = "",
        bibliographic_url: str = "",
        citation_detail: str = "",
        reason: str = "cites",
        label: str = "",  # LPF convention
    ):
        self.id = id
        if short_title:
            self.short_title = short_title
        elif label:
            self.short_title = label
        else:
            self._short_title = ""
        if short_title and label:
            raise ValueError("Cannot specify both short_title and label")
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
        if citation_detail:
            self.citation_detail = citation_detail
        else:
            self._citation_detail = ""
        self.reason = reason

    @property
    def id(self) -> Identifier:
        """Get the citation identifier."""
        return self._id

    @id.setter
    def id(self, id: str | Identifier):
        """Set the citation identifier."""
        if isinstance(id, Identifier):
            self._id = id
        else:
            self._id = make_identifier(id)

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

    @property
    def bibliographic_url(self) -> str:
        """Get the bibliographic URL for the cited work."""
        return str(self._bibliographic_url)

    @bibliographic_url.setter
    def bibliographic_url(self, bibliographic_url: str):
        """Set the bibliographic URL for the cited work."""
        parts = urlparse(bibliographic_url)
        if parts.netloc not in BIBLIOGRAPHIC_URL_NETLOCS:
            raise ValueError(
                f"Bibliographic URL '{bibliographic_url}' must be from a recognized bibliographic service. Recognized domains are: {', '.join(BIBLIOGRAPHIC_URL_NETLOCS)}"
            )
        self._bibliographic_url = URLIdentifier(bibliographic_url)

    @property
    def citation_detail(self) -> str:
        """Get additional citation detail."""
        return self._citation_detail

    @citation_detail.setter
    def citation_detail(self, citation_detail: str):
        """Set additional citation detail."""
        self._citation_detail = normalize_text(citation_detail)

    @property
    def reason(self) -> str:
        """Get the reason for the citation."""
        return self._reason

    @reason.setter
    def reason(self, reason: str):
        """Set the reason for the citation."""
        if reason not in CITATION_TYPES:
            raise ValueError(f"Invalid citation reason: {reason}")
        self._reason = reason

    def asdict(self) -> dict:
        """Return a dictionary representation of the Citation."""
        result = {"@id": str(self.id), "reason": self.reason}
        if self.short_title:
            result["short_title"] = self.short_title
        if self.formatted_citation:
            result["formatted_citation"] = self.formatted_citation
        if self.access_url:
            result["access_url"] = str(self.access_url)
        if self.bibliographic_url:
            result["bibliographic_url"] = str(self.bibliographic_url)
        if self.citation_detail:
            result["citation_detail"] = self.citation_detail
        return result
