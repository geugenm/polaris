"""
Module for testing data.readers.py script.
"""

import pytest

import polaris.data.readers as pldr


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
