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
import re
from validators import url as validate_url

VALID_IDENTIFIER_TYPES = {"url", "alphanumeric", "alphanumeric-delimited"}


def make_identifier(value: str, id_type: str = "") -> "Identifier":
    """
    Factory function to create an Identifier.
    """
    delims = r"\-_,:\."
    delimited_pattern = rf"^[A-Za-z0-9{delims}]+$"
    if id_type == "url":
        return URLIdentifier(value)
    elif id_type == "alphanumeric":
        return Identifier(id_type, value)
    elif id_type == "alphanumeric-delimited":
        return Identifier(id_type, value)
    elif id_type == "":
        if validate_url(value):
            return URLIdentifier(value)
        elif bool(re.match(delimited_pattern, value)):
            return Identifier("alphanumeric-delimited", value)
        else:
            return Identifier("alphanumeric", value)
    else:
        raise ValueError(
            f"Invalid identifier type: '{id_type}'. Expected one of {VALID_IDENTIFIER_TYPES}."
        )


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
