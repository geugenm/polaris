"""
Fixtures for pytest tests
"""

import json

import pytest

from polaris.dataset.dataset import PolarisDataset
from polaris.dataset.frame import PolarisFrame
from polaris.dataset.metadata import PolarisMetadata
from polaris.fetch import data_fetch_decoder


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


POLARIS_METADATA_DICT = {
    'date': 1567460994,
    'cli_options': '',
    'satellite_norad': '44420',
    'satellite_name': 'LightSail-2',
}


@pytest.fixture
def polaris_metadata_dict():
    """PolarisMetadata dict to be used in testing
    """
    return POLARIS_METADATA_DICT


@pytest.fixture
def polaris_metadata_obj():
    """PolarisMetadata obj to be used in testing
    """
    polaris_metadata = PolarisMetadata(POLARIS_METADATA_DICT)
    return polaris_metadata


POLARIS_FRAME_DICT = {
    "time": "2019-07-21 20:43:57",
    "measurement": "",
    "tags": {
        "satellite": "",
        "decoder": "Lightsail2",
        "station": "",
        "observer": "",
        "source": "",
        "version": "0.15.1"
    },
    "fields": {
        "dest_callsign": {
            "value": "N6CP  ",
            "unit": None
        },
        "src_callsign": {
            "value": "KK6HIT",
            "unit": None
        },
        "src_ssid": {
            "value": 2,
            "unit": None
        },
        "dest_ssid": {
            "value": 1,
            "unit": None
        },
        "ctl": {
            "value": 3,
            "unit": None
        },
        "pid": {
            "value": 204,
            "unit": None
        },
        "type": {
            "value": 1,
            "unit": None
        },
        "bat1_volt": {
            "value": 3.875,
            "unit": "V"
        },
        "bat1_temp": {
            "value": 13.0,
            "unit": "degC"
        },
        "bat1_flags": {
            "value": 165,
            "unit": None
        },
        "bat1_ctlflags": {
            "value": 0,
            "unit": None
        }
    }
}


@pytest.fixture
def polaris_frame_dict():
    """PolarisFrame dict to be used in testing
    """
    return POLARIS_FRAME_DICT


POLARIS_FRAME_OBJ = PolarisFrame(POLARIS_FRAME_DICT)


@pytest.fixture
def polaris_frame_obj():
    """PolarisFrame object to be used in testing
    """
    return POLARIS_FRAME_OBJ


POLARIS_DATASET_OBJ = PolarisDataset(metadata=POLARIS_METADATA_DICT,
                                     frames=[POLARIS_FRAME_DICT])


@pytest.fixture
def polaris_dataset_obj():
    """PolarisDataset object to be used in testing
    """
    return POLARIS_DATASET_OBJ


@pytest.fixture
def polaris_dataset_json():
    """PolarisDataset JSON to be used in testing
    """
    return """{
    "metadata": {
        "data_format_version": 1,
        "date": 1567460994,
        "cli_options": "",
        "satellite_norad": "44420",
        "satellite_name": "LightSail-2"
    },
    "frames": [
        {
            "time": "2019-07-21 20:43:57",
            "measurement": "",
            "tags": {
                "satellite": "",
                "decoder": "Lightsail2",
                "station": "",
                "observer": "",
                "source": "",
                "version": "0.15.1"
            },
            "fields": {
                "dest_callsign": {
                    "value": "N6CP  ",
                    "unit": null
                },
                "src_callsign": {
                    "value": "KK6HIT",
                    "unit": null
                },
                "src_ssid": {
                    "value": 2,
                    "unit": null
                },
                "dest_ssid": {
                    "value": 1,
                    "unit": null
                },
                "ctl": {
                    "value": 3,
                    "unit": null
                },
                "pid": {
                    "value": 204,
                    "unit": null
                },
                "type": {
                    "value": 1,
                    "unit": null
                },
                "bat1_volt": {
                    "value": 3.875,
                    "unit": "V"
                },
                "bat1_temp": {
                    "value": 13.0,
                    "unit": "degC"
                },
                "bat1_flags": {
                    "value": 165,
                    "unit": null
                },
                "bat1_ctlflags": {
                    "value": 0,
                    "unit": null
                }
            }
        }
    ]
}"""


@pytest.fixture
def pandas_dataset_dict():
    """PolarisDataset JSON to be used in testing
    """
    return [{
        "dest_callsign": "N6CP  ",
        "src_callsign": "KK6HIT",
        "src_ssid": 2,
        "dest_ssid": 1,
        "ctl": 3,
        "pid": 204,
        "type": 1,
        "bat1_volt": 3.875,
        "bat1_temp": 13.0,
        "bat1_flags": 165,
        "bat1_ctlflags": 0,
        "time": 1563741837
    }]


@pytest.fixture
def polaris_config():
    """Polaris configuration JSON to be used in testing
    """
    return json.dumps({
        'file_layout': {
            'root_dir': '/tmp/polaris'
        },
        'satellite': {
            'name': 'LightSail-2',
            '_comment': 'This is a comment',
            'batch': {
                'fetch': True,
                'learn': True,
                'viz': False
            }
        }
    })


@pytest.fixture
def polaris_config_defaults():
    """Polaris configuration defaults dict to be used in testing
    """
    return {
        'file_layout': {
            'root_dir': '/default_root_dir'
        },
        'satellite': {
            'batch': {
                'fetch': True,
                'learn': True,
                'viz': False
            }
        }
    }
