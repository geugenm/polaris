"""Test for polaris.anomaly.detector
"""

from contextlib import contextmanager

import pandas as pd
import pytest

from polaris.anomaly import detector

SAMPLE_DATA = pd.DataFrame({
    "a": [1, 2, 3, 4, 5],
    "b": [11, 15, 19, 23, 27],
    "c": [50, 100, 150, 200, float("nan")],
    "d": [.5, 1.5, 3.5, 12.5, 15.5],
})


@contextmanager
def does_not_raise():
    """Dummy class for cases where errors are not raise
    """
    yield


def test_processing():
    """Test for apply_preprocessing and remove_preprocessing
    """
    normalizer, pp_data = detector.apply_preprocessing(SAMPLE_DATA)

    rm_pp_data = detector.remove_preprocessing(normalizer, pp_data)

    # As column names are slightly different, we need to copy them over
    rm_pp_data.columns = SAMPLE_DATA.columns

    # Since rm_pp_data may have zero padded layers, take first few rows
    rm_pp_data = rm_pp_data.iloc[:SAMPLE_DATA.shape[0], :]

    # Check if the data is same in both SAMPLE_DATA and rm_pp_data
    # There is a conversion to float during normalization => check_dtype=False
    pd.testing.assert_frame_equal(rm_pp_data, SAMPLE_DATA, check_dtype=False)


@pytest.mark.parametrize("layer_dims, activations, expectation", [
    ([600, 128, 32], ["relu", "relu", "tanh", "sigmoid"], does_not_raise()),
    ([600, 128, 32], None, does_not_raise()),
    ([600, 128, 32], ["relu", "relu", "tanh"], pytest.raises(ValueError)),
])
def test_create_models(layer_dims, activations, expectation):
    """Test for creating models
    """
    with expectation:
        _ = detector.create_models(layer_dims, activations)
