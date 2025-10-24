#
# This file is part of pleiades_lpf
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the gazetteer module.
"""

from langstring import LangString, MultiLangString
from pleiades_lpf.gazetteer import (
    Feature,
    FeatureCollection,
    FeatureType,
    LPFTypeError,
    LPFValueError,
)
from pytest import raises


class TestFeature:
    def test_valid_properties(self):
        """Test that valid properties pass validation."""
        props = {"title": "Test Place", "ccodes": ["US"], "fclasses": ["P"]}
        feature = Feature(properties=props)
        assert feature.properties == props

    def test_invalid_properties_not_dict(self):
        """Test that non-dictionary properties raise an error."""
        with raises(LPFTypeError):
            Feature(properties="not a dict")  # type: ignore

    def test_missing_required_key(self):
        """Test that missing required keys raise an error."""
        props = {
            "title": "Test Place",
            "ccodes": ["US"],
            # Missing 'fclasses'
        }
        with raises(LPFValueError):
            Feature(properties=props)

    def test_invalid_key_type(self):
        """Test that invalid key types raise an error."""
        props = {
            "title": "Test Place",
            "ccodes": "US",  # Should be a list
            "fclasses": ["P"],
        }
        with raises(LPFTypeError):
            Feature(properties=props)

    def test_invalid_list_item_type(self):
        """Test that invalid list item types raise an error."""
        props = {
            "title": "Test Place",
            "ccodes": ["US"],
            "fclasses": [123],  # Should be strings
        }
        with raises(LPFTypeError):
            Feature(properties=props)


class TestFeatureCollection:
    def test_feature_collection_creation(self):
        """Test creating a FeatureCollection with valid features."""
        feature1 = Feature(
            properties={"title": "Place 1", "ccodes": ["US"], "fclasses": ["P"]}
        )
        feature2 = Feature(
            properties={"title": "Place 2", "ccodes": ["FR"], "fclasses": ["A"]}
        )
        fc = FeatureCollection(features=[feature1, feature2])
        assert len(fc.features) == 2
        assert fc.features[0].properties["title"] == "Place 1"
        assert fc.features[1].properties["title"] == "Place 2"


class TestFeatureType:
    def test_fc_creation(self):
        """Test creating a FeatureClass with citations and aliases."""
        cit = {
            "id": "cite-001",
            "short_title": "Wikidata",
            "formatted_citation": "Wikidata: The Free Knowledge Base That Anyone Can Edit. Wikimedia Foundation, 2014-. https://www.wikidata.org/.",
            "access_url": "https://www.wikidata.org/wiki/Q486972",
            "bibliographic_url": "https://www.zotero.org/groups/2533/items/BCQIKDKS",
            "citation_detail": " human settlement (Q486972)",
        }
        ft = FeatureType(
            id="https://www.wikidata.org/wiki/Q486972",
            label="human settlement",
            label_lang="en",
            aliases=[
                {"text": "inhabited place", "lang": "en"},
                LangString("asentamiento", "es"),
            ],
            citations=[cit],
        )
        assert ft.id == "https://www.wikidata.org/wiki/Q486972"
        assert ft.label.text == "human settlement"
        assert ft.label.lang == "en"
        assert len(ft.aliases) == 2
        assert isinstance(ft.aliases, MultiLangString)
        assert ft.aliases["en"] == {"inhabited place"}
        assert ft.aliases["es"] == {"asentamiento"}
        assert len(ft.citations) == 1
        assert str(ft.citations[0].id) == "cite-001"
        assert ft.citations[0].access_url == "https://www.wikidata.org/wiki/Q486972"
        assert (
            ft.citations[0].bibliographic_url
            == "https://www.zotero.org/groups/2533/items/BCQIKDKS"
        )
        assert (
            ft.citations[0].formatted_citation
            == "Wikidata: The Free Knowledge Base That Anyone Can Edit. Wikimedia Foundation, 2014-. https://www.wikidata.org/."
        )
        assert (
            ft.citations[0].citation_detail == "human settlement (Q486972)"
        )  # NB space normalized
