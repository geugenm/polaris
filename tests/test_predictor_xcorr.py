"""
`pytest` testing framework file for xcorr predictor
"""

import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from polaris.learn.predictor.cross_correlation import XCorr


def test_xcorr():
    """
    `pytest` entry point
    """

    test_df = pd.DataFrame({
        "A": [4, 123, 24.2, 3.14, 1.41],
        "B": [7, 0, 24.2, 3.14, 8.2]
    })
    correlator = XCorr()
    assert correlator.importances_map is None

    correlator.fit(test_df)
    assert correlator.importances_map is not None
    assert isinstance(correlator.importances_map, pd.DataFrame)
    assert correlator.importances_map.shape[0] == 2
    assert (correlator.importances_map.shape[1] ==
            correlator.importances_map.shape[0])


def test_xcorr_pipeline():
    """
    `pytest` entry point
    """

    pipeline = Pipeline([("deps", XCorr())])

    assert pipeline is not None


def test_gridsearch_happy():
    """
    Test happy path for gridsearch
    """
    test_df = pd.DataFrame({
        "A": [4, 123, 24.2, 3.14, 1.41],
        "B": [7, 0, 24.2, 3.14, 8.2]
    })

    xcorr_params = {
        "random_state": 42,
        "test_size": 0.1,
        "gridsearch_scoring": "neg_mean_squared_error",
        # The split number was obtained through trial-and-error,
        # it shoud be reviewed in the future to adapt to
        # the targeted satellite.
        "gridsearch_n_splits": 2
    }

    correlator = XCorr(use_gridsearch=True, xcorr_params=xcorr_params)
    correlator.fit(test_df)
    assert correlator.importances_map is not None
    assert isinstance(correlator.importances_map, pd.DataFrame)
    assert correlator.importances_map.shape[0] == 2
    assert (correlator.importances_map.shape[1] ==
            correlator.importances_map.shape[0])


def test_gridsearch_incompatible_input():
    """
    Test incompatible input for gridsearch
    """
    test_df = [1, 2, 3, 4]

    correlator = XCorr(use_gridsearch=True)
    with pytest.raises(TypeError):
        correlator.fit(test_df)
