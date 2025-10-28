#
# This file is part of pleiades_lpf
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define the underlying gazetteer data structure for Pleiades LPF.
"""
from langstring import LangString, MultiLangString, Controller, GlobalFlag
import logging
from pprint import pformat
import re
from shapely.geometry import shape
from slugify import slugify
from typing import override

from .aat import AATMatcher
from .citations import Citation
from .identifiers import Identifier, make_identifier
from .text import normalize_text

# set default rules for LangStrings
for true_flag in [
    GlobalFlag.VALID_LANG,
    GlobalFlag.LOWERCASE_LANG,
    GlobalFlag.DEFINED_TEXT,
    GlobalFlag.DEFINED_LANG,
]:
    Controller.set_flag(true_flag, True)


logger = logging.getLogger(__name__)
rx_lang_string = re.compile(r"^(?P<text>[^@]+?)(@(?P<lang>[a-zA-Z\-]+))?$")
GEOMETRY_TYPES = {
    "Point",
    "MultiPoint",
    "LineString",
    "MultiLineString",
    "Polygon",
    "MultiPolygon",
    "GeometryCollection",
}
CERTAINTY_LEVELS = {"certain", "less-certain", "uncertain"}


class LPFValueError(ValueError):
    """Custom exception for LPF value errors."""

    pass


class LPFTypeError(TypeError):
    """Custom exception for LPF type errors."""

    pass


class When:
    """
    LPF When.
    """

    def __init__(self, earliest: str = "", latest: str = ""):
        pass


class Geometry:
    """
    GeoJSON Geometry.
    https://datatracker.ietf.org/doc/html/rfc7946#section-3.1
    """

    def __init__(
        self,
        type: str,
        coordinates: list = [],
        certainty: str | None = None,
        when: When | dict = dict(),
        **kwargs,
    ):
        # GeoJSON spec
        self._shape = shape({"type": type, "coordinates": coordinates})

        # LPF extension
        self._certainty = None
        if certainty is not None:
            self.certainty = certainty  # LPF extension to GeoJSON
        if when:
            raise NotImplementedError("Geometry:when is not yet implemented")
        if kwargs:
            logger.warning(f"ignoring unexpected kwargs: {pformat(kwargs, indent=2)}")

    @property
    def certainty(self):
        return self._certainty

    @certainty.setter
    def certainty(self, certainty: str | None):
        if certainty not in CERTAINTY_LEVELS:
            raise LPFValueError(
                f"Geometry:certainty must be one of {CERTAINTY_LEVELS}, not '{certainty}'"
            )
        self._certainty = certainty

    @property
    def coordinates(self):
        return self._shape.__geo_interface__["coordinates"]

    @property
    def type(self):
        return self._shape.geom_type

    def asdict(self):
        """Return a dictionary representation of the Geometry."""
        d = {"type": self.type, "coordinates": self.coordinates}
        if self.certainty is not None:
            d["certainty"] = self.certainty
        return d


class Feature:
    """
    GeoJSON Feature.
    https://datatracker.ietf.org/doc/html/rfc7946#section-3.2
    """

    def __init__(
        self,
        geometry: Geometry | dict | None = None,
        properties: dict = dict(),
        id: str | int | None = None,
        types: list[FeatureType | dict] = [],
        **kwargs,  # kwargs are ignored
    ):

        # GeoJSON spec
        self._type = "Feature"  # Fixed value
        self._geometry = None  # Geometry object or None
        if geometry:
            self.geometry = geometry
        if properties:
            self._validate_properties(properties)
        self.properties = properties  # Dictionary of properties
        self.id = id  # Optional identifier (string or number)

        # LPF extensions
        self.when = dict()  # Temporal information
        self.names = []  # List of names
        self.types = types  # List of types
        self.links = []  # List of links to other resources
        self.relations = []  # List of relations to other features
        self.descriptions = []  # List of descriptions
        self.depictions = []  # List of depictions (e.g., images)

    def asdict(self):
        """Return a dictionary representation of the Feature."""
        result = {
            "types": self.types,
            "properties": self.properties,
            # "geometry": self.geometry,
            # "when": self.when,
            # "names": self.names,
            # "types": self.types,
            # "links": self.links,
            # "relations": self.relations,
            # "descriptions": self.descriptions,
            # "depictions": self.depictions,
        }
        if self.id is not None:
            result["@id"] = self.id  # LPF uses @id for identifiers
        return result

    def augment(self):
        """Augment the Feature."""
        # Augment each FeatureType
        for ft in self.types:
            ft.augment()

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, geometry: Geometry | dict):
        """Set the Geometry object."""
        if isinstance(geometry, dict):
            self._geometry = Geometry(**geometry)
        elif isinstance(geometry, Geometry):
            self._geometry = geometry
        else:
            raise LPFTypeError(
                f"Feature:geometry must be a Geometry object or a dict, not {type(geometry)}"
            )

    @property
    def types(self):
        return self._types

    @types.setter
    def types(self, types: list[FeatureType | dict]):
        """Set the list of feature types."""
        if not isinstance(types, list):
            raise LPFTypeError(
                f"Feature:types must be a list of FeatureType objects or dicts, not {type(types)}"
            )
        self._types = []
        for i, t in enumerate(types):
            if isinstance(t, dict):
                self._types.append(FeatureType(**t))
            elif isinstance(t, FeatureType):
                self._types.append(t)
            else:
                raise LPFTypeError(
                    f"Feature:types must be a list of FeatureType objects or dicts, found {type(t)} in position {i}"
                )

    def _validate_properties(self, properties: dict = dict()):
        """
        Validate a properties dictionary according to LPF specifications:
        "properties":{
            "title": "Abingdon (UK)",
            "ccodes": ["GB"],
            "fclasses": ["P"]
        }
        """
        # Validate that properties is a dictionary
        if not isinstance(properties, dict):
            raise LPFTypeError(
                f"Feature:properties must be a dictionary, not {type(properties)}"
            )

        # Validate required keys and their types
        expected = {"title": str, "ccodes": list, "fclasses": list}
        for key, expected_type in expected.items():
            if key not in properties:
                raise LPFValueError(
                    f"Feature:properties is missing required key: {key}"
                )
            if not isinstance(properties[key], expected_type):
                raise LPFTypeError(
                    f"Feature:properties[{key}] must be of type {expected_type}, not {type(properties[key])}"
                )
        # Validate types of individual items in ccodes and fclasses
        expected = {"ccodes": str, "fclasses": str}
        for key, expected_subtype in expected.items():
            for i, item in enumerate(properties.get(key, [])):
                if not isinstance(item, expected_subtype):
                    raise LPFTypeError(
                        f"Feature:properties[{key}] must be a list of {expected_subtype}, found {type(item)} in position {i}"
                    )
        # Warn that actual values of ccodes are not validated
        logger.warning(
            "Country codes in Feature:properties['ccodes'] are not validated."
        )

        # Validate the actual values of fclasses against those allowed by the LPF spec
        VALID_FCLASSES = {
            "A": "Administrative entities (e.g. countries, provinces, municipalities)",
            "H": "Water bodies (e.g. rivers, lakes, bays, seas)",
            "L": "Regions, landscape areas (cultural, geographic, historical)",
            "P": "Populated places (e.g. cities, towns, hamlets)",
            "R": "Roads, routes, rail",
            "S": "Sites (e.g. archaeological sites, buildings, complexes)",
            "T": "Terrestrial landforms (e.g. mountains, valleys, capes)",
        }
        for i, fclass in enumerate(properties.get("fclasses", [])):
            if fclass not in VALID_FCLASSES:
                raise LPFValueError(
                    f"Feature:properties['fclasses'] contains invalid fclass '{fclass}' in position {i}. Valid fclasses are: {list(VALID_FCLASSES.keys())}"
                )


class FeatureCollection:
    """
    GeoJSON Features collection.
    https://datatracker.ietf.org/doc/html/rfc7946#section-3.3
    """

    DEFAULT_LPF_CONTEXT = "https://raw.githubusercontent.com/LinkedPasts/linked-places/master/linkedplaces-context-v1.1.jsonld"

    def __init__(
        self,
        context: str = DEFAULT_LPF_CONTEXT,
        features: list = [Feature | dict],
        **kwargs,
    ):  # kwargs are ignored
        # GeoJSON spec
        self._type = "FeatureCollection"  # Fixed value
        self.features = []  # List of Feature objects
        for f in features:
            if isinstance(f, dict):
                self.features.append(Feature(**f))
            elif isinstance(f, Feature):
                self.features.append(f)
            else:
                raise LPFTypeError(
                    f"FeatureCollection:features must be a list of Feature objects or dicts, found {type(f)}"
                )

        # LPF extension
        self.context = context  # LPF context URI

    def asdict(self):
        """Return a dictionary representation of the FeatureCollection."""
        return {
            "type": self.type,
            "features": [f.asdict() for f in self.features],
            "@context": self.context,
        }

    def augment(self):
        """Augment the FeatureCollection and its Features."""
        for feature in self.features:
            feature.augment()

    @property
    def type(self):
        return self._type


class FeatureType:
    """
    LPF Feature Type.
    """

    def __init__(
        self,
        label: LangString | str | dict,
        label_lang: str = "",
        citations: list[Citation | dict] = [],
        aliases: list[LangString | str | dict] = [],
        when: When | dict = dict(),
        sourceLabels: list[LangString | str | dict] = [],  # lpf v1 (stored as aliases)
        sourceLabel: str = "",  # whg variant (treated as an alias)
        identifier: str = "",  # lpf v1 (stored as id)
        id: str | Identifier = "",  # pleiades extension: alternative to identifier
        **kwargs,  # kwargs are ignored
    ):
        if kwargs:
            logger.warning(f"ignoring unexpected kwargs: {pformat(kwargs, indent=2)}")

        # tools for augmentation if needed
        self._aat_matcher = AATMatcher()

        # LPF v1 "label"
        if not label and not sourceLabel:
            raise LPFValueError(
                "FeatureType: either label or sourceLabel must be provided"
            )
        if sourceLabel and not label:
            # use sourceLabel as label if no label provided (WHG variant)
            self.set_label(sourceLabel)
        else:
            self.set_label(label, label_lang)

        # LPF v1 "identifier"
        if not id and not identifier:
            # generate id from label
            generated_id = slugify(self.label.text)
            logger.warning(
                f"FeatureType: no id or identifier provided, generating id '{generated_id}' from label '{self.label.text}'"
            )
            self.id = generated_id
        elif not id and identifier:
            # LPF v1 identifier provided
            self.id = identifier
        elif id and not identifier:
            # Pleiades variant id provided
            self.id = id
        elif isinstance(id, str) and id == identifier:
            # both provided and match (id is a string)
            self.id = id
        elif isinstance(id, Identifier) and str(id) == identifier:
            # both provided and match (id is an Identifier)
            self.id = id
        else:
            raise LPFValueError(
                f"FeatureType id ({id}) and identifier ({identifier}) do not match"
            )

        # Pleiades variant: citations
        self._citations = []
        if citations:
            self.citations = citations
        else:
            self._citations = []

        # LPF v1 sourceLabels (Pleiades variant aliases)
        self._aliases = MultiLangString()
        if aliases:
            self.set_aliases(aliases)
        elif sourceLabels:
            self.set_aliases(sourceLabels)
        elif aliases and sourceLabels:
            self.set_aliases(aliases)
            for sl in sourceLabels:
                self.add_alias(sl)
        if label and sourceLabel and label != sourceLabel:
            # treat sourceLabel as an alias
            self.add_alias(sourceLabel)

    def augment(self):
        """Augment the FeatureType."""
        # Example augmentation: match label against AAT terms
        matched_aat_ids = self._aat_matcher.match(self.label, self.aliases)
        match_len = len(matched_aat_ids)
        if match_len == 0:
            return
        if match_len == 1:
            matched_aat_id = matched_aat_ids[0]

        elif "300008347" in [maid[0] for maid in matched_aat_ids]:
            # prefer "settlement" if multiple matches
            matched_aat_id = ("300008347", "inhabited places")
        else:
            raise NotImplementedError(
                f"FeatureType '{self.label.text}' matched multiple AAT term IDs: {matched_aat_ids}"
            )
        citation = Citation(
            id=f"aat:{matched_aat_id[0]}",
            short_title="Getty AAT",
            formatted_citation="The Getty Research Institute. “Art & Architecture Thesaurus.” 2017. https://www.getty.edu/research/tools/vocabularies/aat/.",
            access_url=f"https://vocab.getty.edu/aat/{matched_aat_id[0]}",
            bibliographic_url="https://www.zotero.org/groups/2533/items/FLDP5U84",
            citation_detail=f"{matched_aat_id[0]}: {matched_aat_id[1]}",
            reason="closeMatch",
        )
        self.add_citation(citation)

    @property
    def id(self) -> str:
        """Get the feature type identifier."""
        return str(self._id)

    @id.setter
    def id(self, id: str | Identifier):
        """Set the feature type identifier."""
        if isinstance(id, Identifier):
            self._id = id
        elif isinstance(id, str):
            self._id = make_identifier(id)

    @property
    def label(self) -> LangString:
        """Get the feature type label."""
        return self._label

    @label.setter
    def label(self, label: str | LangString):
        """Set the feature type label."""
        self.set_label(label)

    def set_label(self, label: str | LangString | dict, lang_tag: str = ""):
        """Set the feature type label."""
        if not label:
            return
        if isinstance(label, LangString):
            if lang_tag:
                if lang_tag != "und" and label.lang == "und":
                    # set the language tag if label lang is undefined
                    label.lang = lang_tag
                elif lang_tag != label.lang:
                    raise LPFValueError(
                        "FeatureType:label_lang does not match LangString language tag"
                    )
            self._label = LangString(normalize_text(label.text.lower()), label.lang)
        elif isinstance(label, str):
            if not lang_tag:
                m = rx_lang_string.match(label)
                if m:
                    # handle "label@lang" format
                    label = m.group("text")
                    lang_tag = m.group("lang")
            if lang_tag:
                self._label = LangString(normalize_text(label.lower()), lang_tag)  # type: ignore
            else:
                self._label = LangString(normalize_text(label.lower()), "und")  # type: ignore
        elif isinstance(label, dict):
            self._label = LangString(
                normalize_text(label.get("text", "")).lower(), label.get("lang", "und")
            )
        else:
            raise LPFTypeError(
                f"FeatureType:label must be a string or LangString, not {type(label)}"
            )

    @property
    def citations(self) -> list[Citation]:
        """Get the list of citations."""
        return self._citations

    @citations.setter
    def citations(self, citations: list[Citation | dict]):
        """Set the list of citations."""
        if not isinstance(citations, list):
            raise LPFTypeError(
                f"FeatureType:citations must be a list of Citation objects, not {type(citations)}"
            )
        self._citations = []
        for idx, citation in enumerate(citations):
            if isinstance(citation, dict):
                self._citations.append(Citation(**citation))
            elif isinstance(citation, Citation):
                self._citations.append(citation)
            else:
                raise LPFTypeError(
                    f"FeatureType:citations must be a list of Citation objects, found {type(citation)} in position {idx}"
                )

    def add_citation(self, citation: Citation | dict):
        """Add a single citation."""
        if isinstance(citation, dict):
            self._citations.append(Citation(**citation))
        elif isinstance(citation, Citation):
            self._citations.append(citation)
        else:
            raise LPFTypeError(
                f"FeatureType:citations must be Citation objects, not {type(citation)}"
            )

    @property
    def aliases(self) -> MultiLangString:
        """Get the list of aliases."""
        return self._aliases

    def add_alias(self, alias: str | LangString | dict, lang: str = "und"):
        """Add a single alias."""
        if isinstance(alias, LangString):
            self._aliases.add_langstring(
                LangString(normalize_text(alias.text), alias.lang)
            )
        elif isinstance(alias, str):
            m = rx_lang_string.match(alias)
            if m:
                # handle "alias@lang" format
                alias = m.group("text")
                lang = m.group("lang")
            if lang:
                self._aliases.add_langstring(LangString(normalize_text(alias), lang))  # type: ignore
            else:
                self._aliases.add_langstring(LangString(normalize_text(alias), "und"))  # type: ignore
        elif isinstance(alias, dict):
            self._aliases.add_langstring(
                LangString(
                    normalize_text(alias.get("text", "")),
                    alias.get("lang", "und"),
                )
            )
        else:
            raise LPFTypeError(
                f"FeatureType:aliases must be strings or LangStrings, found {type(alias)}"
            )

    def set_aliases(
        self, aliases: list[str | LangString | dict] | MultiLangString | dict
    ):
        """Set the list of aliases."""

        self._aliases = MultiLangString()
        if isinstance(aliases, MultiLangString):
            for s in aliases.to_langstrings():
                self.add_alias(s)
        elif isinstance(aliases, dict):
            for lang, lstrings in aliases.items():
                for lstr in lstrings:
                    self.add_alias(lstr, lang)
        elif not isinstance(aliases, list):
            raise LPFTypeError(
                f"FeatureType:aliases must be a list of strings, not {type(aliases)}"
            )
        for alias in aliases:
            self.add_alias(alias)

    @property
    def when(self) -> When:
        """Get the When object."""
        return self._when

    @when.setter
    def when(self, when: When | dict):
        """Set the When object."""
        if isinstance(when, When):
            self._when = when
        elif isinstance(when, dict):
            self._when = When(**when)
        else:
            raise LPFTypeError(
                f"FeatureType:when must be a When object or a dict, not {type(when)}"
            )

    def asdict(self, mode="full") -> dict:
        """Return a dictionary representation of the FeatureType."""
        source_labels = [
            {"label": alias.text, "lang": alias.lang}
            for alias in self.aliases.to_langstrings()
        ]
        source_labels.append({"label": self.label.text, "lang": self.label.lang})
        result = {
            "identifier": str(self.id),
            "label": self.label.text,
            "sourceLabels": source_labels,
            "when": None,  # implement when.asdict() when When is implemented
        }
        if mode == "full":
            result["citations"] = [citation.asdict() for citation in self.citations]
            result["aliases"] = [
                {"label": alias.text, "lang": alias.lang}
                for alias in self.aliases.to_langstrings()
            ]

        if self.id:
            result["@id"] = str(self.id)
        return result
