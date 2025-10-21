#
# This file is part of pleiades_lpf
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define the underlying gazetteer data structure for Pleiades LPF.
"""
import logging

logger = logging.getLogger(__name__)


class LPFValidationError(Exception):
    """Custom exception for LPF validation errors."""

    pass


class Geometry:
    """
    GeoJSON Geometry.
    https://datatracker.ietf.org/doc/html/rfc7946#section-3.1
    """

    def __init__(self):
        pass


class Feature:
    """
    GeoJSON Feature.
    https://datatracker.ietf.org/doc/html/rfc7946#section-3.2
    """

    def __init__(
        self,
        geometry: Geometry | None = None,
        properties: dict = dict(),
        id: str | int | None = None,
        **kwargs,  # kwargs are ignored
    ):
        # GeoJSON spec
        self._type = "Feature"  # Fixed value
        self.geometry = geometry  # Geometry object or None
        if properties:
            self._validate_properties(properties)
        self.properties = properties  # Dictionary of properties
        self.id = id  # Optional identifier (string or number)

        # LPF extensions
        self.when = dict()  # Temporal information
        self.names = []  # List of names
        self.types = []  # List of types
        self.links = []  # List of links to other resources
        self.relations = []  # List of relations to other features
        self.descriptions = []  # List of descriptions
        self.depictions = []  # List of depictions (e.g., images)

    def asdict(self):
        """Return a dictionary representation of the Feature."""
        result = {
            "type": self.type,
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

    @property
    def type(self):
        return self._type

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
            raise TypeError(
                f"Feature:properties must be a dictionary, not {type(properties)}"
            )

        # Validate required keys and their types
        expected = {"title": str, "ccodes": list, "fclasses": list}
        for key, expected_type in expected.items():
            if key not in properties:
                raise LPFValidationError(
                    f"Feature:properties is missing required key: {key}"
                )
            if not isinstance(properties[key], expected_type):
                raise TypeError(
                    f"Feature:properties[{key}] must be of type {expected_type}, not {type(properties[key])}"
                )
        # Validate types of individual items in ccodes and fclasses
        expected = {"ccodes": str, "fclasses": str}
        for key, expected_subtype in expected.items():
            for i, item in enumerate(properties.get(key, [])):
                if not isinstance(item, expected_subtype):
                    raise TypeError(
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
                raise LPFValidationError(
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
                raise TypeError(
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

    @property
    def type(self):
        return self._type
