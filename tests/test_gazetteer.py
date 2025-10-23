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
    FeatureClass,
    FeatureCollection,
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


class TestFeatureClass:
    def test_fc_creation(self):
        fc = FeatureClass("foo", "bar")
        assert isinstance(fc, FeatureClass)
        label = fc.label
        assert isinstance(label, LangString)
        assert label == "bar"
        assert label.lang == "und"
        fc.add_alias("baz", "en")
        assert len(fc.aliases) == 1
        assert isinstance(fc.aliases, MultiLangString)
        for s in fc.aliases.get_texts():
            assert s in ["baz"]
