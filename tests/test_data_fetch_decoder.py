"""
pytest testing framework for data_fetch module
"""

import pytest
from polaris.data_fetch import data_fetch_decoder


def test_find_satellite_happy(satellite_list):
    """Test happy path for find_satellite()
    """
    # test_satellite = 'LightSail-2'
    test_satellite = 'ExampleSat'
    sat = data_fetch_decoder.find_satellite(test_satellite, satellite_list)
    assert isinstance(sat, data_fetch_decoder.Satellite)


def test_find_satellite_sad(satellite_list):
    """Test sad path for find_satellite()
    """
    test_satellite = 'DoesNotExist'
    with pytest.raises(data_fetch_decoder.NoSuchSatellite):
        _ = data_fetch_decoder.find_satellite(test_satellite, satellite_list)


def test_find_satellite_no_decoder(satellite_list):
    """Test no_decoder path for find_satellite()
    """
    test_satellite = 'NoDecoderSatellite'
    with pytest.raises(data_fetch_decoder.NoDecoderForSatellite):
        _ = data_fetch_decoder.find_satellite(test_satellite, satellite_list)
