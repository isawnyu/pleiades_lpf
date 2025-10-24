#
# This file is part of pleiades_lpf
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test loading/dumping.
"""
import json
from pathlib import Path
from pleiades_lpf import dump, dumps, load, loads
from pleiades_lpf.gazetteer import FeatureCollection, FeatureType
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
        import logging
        from pprint import pformat

        logger = logging.getLogger(__name__)
        logger.debug(pformat([t.asdict() for t in f.types], indent=2))
        # assert f.types
        # add more here as gazetteer module is expanded
