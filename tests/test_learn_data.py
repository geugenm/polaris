"""
Module for testing learn.data.readers.py script.
"""
import json

import polaris.learn.data.readers as pldr


def test_fetch_json_to_pandas_json(polaris_dataset_json, pandas_dataset_dict):
    """Test dataset to_json() method
    """
    polaris_dataset_dict = json.loads(polaris_dataset_json)
    assert pandas_dataset_dict == pldr.records_from_satnogs_frames(
        polaris_dataset_dict)


def test_read_polaris_data():
    """ Test file reading function
    """
    source_none, none_output = pldr.read_polaris_data(
        "/tmp/tmp/tmp/a/b/a/b/NOTINSPACE")
    assert none_output is None
    assert source_none is None
