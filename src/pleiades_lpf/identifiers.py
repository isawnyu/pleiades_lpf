#
# This file is part of pleiades_lpf
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define identification classes
"""
from .text import normalize_text
from validators import url as validate_url

VALID_IDENTIFIER_TYPES = {"url", "alphanumeric"}


class Identifier:
    """
    An identifier is a string value with a particular type.
    """

    def __init__(self, id_type: str, value: str):
        self._type = ""
        self._value = ""
        self.id_type = id_type
        self.id_value = value

    @property
    def id_type(self) -> str:
        """Get the identifier type."""
        return self._type

    @id_type.setter
    def id_type(self, id_type: str):
        """Set the identifier type."""
        id_type = normalize_text(id_type)
        if id_type not in VALID_IDENTIFIER_TYPES:
            raise ValueError(
                f"Invalid identifier type: '{id_type}'. Expected one of {VALID_IDENTIFIER_TYPES}."
            )
        self._type = id_type

    @property
    def id_value(self) -> str:
        """Get the identifier value."""
        return self._value

    @id_value.setter
    def id_value(self, value: str):
        """Set the identifier value."""
        if not isinstance(value, str):
            raise TypeError(f"Identifier value must be a string. Got '{type(value)}'")
        value = value.strip()
        if self._type == "alphanumeric" and not value.isalnum():
            raise ValueError(
                f"Alphanumeric identifier value '{value}' must contain only letters and numbers."
            )
        elif self._type == "url" and not validate_url(value):
            raise ValueError(f"URL identifier value '{value}' must be a valid URL.")
        self._value = normalize_text(value)

    def __str__(self) -> str:
        return self.id_value


class URLIdentifier(Identifier):
    """
    An identifier that is a URL.
    """

    def __init__(self, url: str):
        Identifier.__init__(self, id_type="url", value=url)
