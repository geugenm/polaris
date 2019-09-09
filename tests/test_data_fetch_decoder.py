"""
pytest testing framework for data_fetch module
"""

import datetime

import pytest

from contrib.normalizers.common import Field, Normalizer
from polaris.data_fetch import data_fetch_decoder


class FixtureNormalizer(Normalizer):
    """Normalizer fixture for pytest
    """

    def __init__(self):
        super().__init__()
        self.normalizers = [
            Field('example_telemetry', lambda x: x, None, 'Example Telemetry')
        ]


SINGLE_FRAME = [
    {
        "time": "2019-01-01 00:00:00",
        "fields": {
            'example_telemetry': 0
        }
    },
]

MULTIPLE_FRAMES = [{
    "time": "2019-01-01 00:00:00",
    "fields": {
        'example_telemetry': 0
    }
}, {
    "time": "2019-01-01 01:00:00",
    "fields": {
        'example_telemetry': 1
    }
}, {
    "time": "2019-01-01 02:00:00",
    "fields": {
        'example_telemetry': 2
    }
}]


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


def test_load_normalizer_no_normalizer(satellite_list):
    """Test no_normlizer path for find_satellite()
    """
    test_satellite = satellite_list[2]
    with pytest.raises(data_fetch_decoder.NoNormalizerForSatellite):
        _ = data_fetch_decoder.load_normalizer(test_satellite)


def test_build_dates_from_string():
    """Test dates conversion for build_start_and_end_dates()
    """
    start_date_str = '2019-08-14'
    end_date_str = '2019-08-16'
    start_date, end_date = data_fetch_decoder.build_start_and_end_dates(
        start_date_str, end_date_str)
    assert end_date - start_date == datetime.timedelta(days=2)


def test_build_dates_from_default():
    """Test default dates generation for build_start_and_end_dates()
    """
    start_date, end_date = data_fetch_decoder.build_start_and_end_dates(
        None, None)
    assert end_date - start_date == datetime.timedelta(seconds=3600)


def test_data_normalize_empty_list():
    """Test data_normalize() with empty list of frames
    """
    frame_list = []

    normalized_frames = data_fetch_decoder.data_normalize(
        FixtureNormalizer(), frame_list)
    assert normalized_frames == []


def test_data_normalize_happy_path_single_frame():
    """Test data_normalize() happy path with single frame
    """

    normalized_frames = data_fetch_decoder.data_normalize(
        FixtureNormalizer(), SINGLE_FRAME)

    assert len(normalized_frames) == 1
    assert normalized_frames[0]['fields'] == {
        'example_telemetry': {
            'value': 0,
            'unit': None
        }
    }


def test_data_normalize_happy_path_multiple_frames():
    """Test data_normalize() happy path with multiple_frames
    """

    normalized_frames = data_fetch_decoder.data_normalize(
        FixtureNormalizer(), MULTIPLE_FRAMES)

    assert len(normalized_frames) == 3
    for i in range(len(normalized_frames)):  # pylint: disable=C0103,C0200
        assert normalized_frames[i]['fields'] == {
            'example_telemetry': {
                'value': i,
                'unit': None
            }
        }
