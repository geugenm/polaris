"""
Module for testing learn.data.readers.py script.
"""
import json

import pytest

import polaris.learn.data.readers as pldr


def test_fetch_json_to_pandas_json(polaris_dataset_json, pandas_dataset_dict):
    """Test dataset to_json() method
    """
    polaris_dataset_dict = json.loads(polaris_dataset_json)
    assert pandas_dataset_dict == pldr.records_from_satnogs_frames(
        polaris_dataset_dict)


def test_read_polaris_data_missing_file():
    """Test reading polaris data, missing file
    """
    with pytest.raises(FileNotFoundError):
        _, _ = pldr.read_polaris_data("/tmp/tmp/tmp/a/b/a/b/NOTINSPACE.csv")
    with pytest.raises(FileNotFoundError):
        _, _ = pldr.read_polaris_data("/tmp/tmp/tmp/a/b/a/b/NOTINSPACE.json")


def test_read_polaris_data_unknown_format():
    """Test reading polaris data, unknown format
    """
    with pytest.raises(pldr.PolarisUnknownFileFormatError):
        _, _ = pldr.read_polaris_data("/tmp/tmp/tmp/a/b/a/b/NOTINSPACE")
