#
# This file is part of pleiades_lpf
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test loading/dumping.
"""
from pathlib import Path
from pleiades_lpf import dump, dumps, load, loads
from pleiades_lpf.gazetteer import FeatureCollection, LPFValidationError
from pytest import raises

test_data_dir = Path(__file__).parent / "data"


class TestModule:
    def test_load(self):
        """Test loading LPF from a file."""
        filename = "whg_7637009.json"
        filepath = test_data_dir / filename
        with open(filepath, "r", encoding="utf-8") as f:
            obj = load(f)
        del f
        assert isinstance(obj, dict)
        fc = FeatureCollection(**obj)
        assert isinstance(fc, FeatureCollection)
        assert len(fc.features) == 1
        f = fc.features[0]
        assert f.properties["title"] == "Rahat Salak"
        assert f.properties["ccodes"] == ["TD"]
        assert f.properties["fclasses"] == []
        # add more here as gazetteer module is expanded
