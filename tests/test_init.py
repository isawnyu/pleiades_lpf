#
# This file is part of pleiades_lpf
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test loading/dumping.
"""
from copy import deepcopy
import json
import logging
from pathlib import Path
from pleiades_lpf import dump, dumps, load, loads
from pleiades_lpf.gazetteer import FeatureCollection, FeatureType, Geometry
from pprint import pformat
from pytest import raises

test_data_dir = Path(__file__).parent / "data"


class TestModule:
    def test_load(self):
        """Test loading LPF from a file."""
        filename = "whg_7637009.json"
        filepath = test_data_dir / filename
        with open(filepath, "r", encoding="utf-8") as f:
            fc = load(f)
        del f
        assert isinstance(fc, FeatureCollection)
        assert isinstance(fc, FeatureCollection)
        assert len(fc.features) == 1

        f = fc.features[0]

        assert f.properties["title"] == "Rahat Salak"
        assert f.properties["ccodes"] == ["TD"]
        assert f.properties["fclasses"] == []

        assert isinstance(f.types, list)
        for ft in f.types:
            assert isinstance(ft, FeatureType)
        assert len(f.types) == 1
        assert f.types[0].label == "settlement"

        assert isinstance(f.geometry, Geometry)
        assert f.geometry.type == "Point"
        assert f.geometry.coordinates == (18.1333333, 14.2333333)
        import logging
        from pprint import pformat

        logger = logging.getLogger(__name__)
        logger.debug(pformat(fc.asdict(), indent=2))


class TestAugment:
    def test_augment_fc(self):
        """Test augmenting FeatureCollection."""
        filename = "whg_7637009.json"
        filepath = test_data_dir / filename
        with open(filepath, "r", encoding="utf-8") as f:
            fcoll = load(f)
        del f
        assert len(fcoll.features[0].types[0].citations) == 0
        fcoll.augment()
        assert len(fcoll.features[0].types[0].citations) == 1
        c = fcoll.features[0].types[0].citations[0]
        assert c.short_title == "Getty AAT"
        logger = logging.getLogger(__name__)
        logger.debug(pformat(fcoll.asdict(), indent=2))
