"""
Module for testing learning.data.readers.py script.
"""
import json

import polaris.learning.data.readers as pldr


def test_fetch_json_to_pandas_json(polaris_dataset_json, pandas_dataset_dict):
    """Test dataset to_json() method
    """
    polaris_dataset_dict = json.loads(polaris_dataset_json)
    assert pandas_dataset_dict == pldr.records_from_satnogs_frames(
        polaris_dataset_dict)
