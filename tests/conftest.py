"""
Fixtures for pytest tests
"""

import pytest

from polaris.data_fetch import data_fetch_decoder


@pytest.fixture
def satellite_list():
    """List of satellites to be used in testing
    """
    return [
        data_fetch_decoder.Satellite(name='ExampleSat',
                                     norad_id='12345',
                                     decoder='ExampleDecoder',
                                     normalizer='ExampleNormalizer'),
        data_fetch_decoder.Satellite(name='NoDecoderSatellite',
                                     norad_id='67890',
                                     decoder=None,
                                     normalizer='ExampleNormalizer'),
        data_fetch_decoder.Satellite(name='NoNormalizerSatellite',
                                     norad_id='67890',
                                     decoder='ExampleNormalizer',
                                     normalizer=None)
    ]
