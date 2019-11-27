"""
`pytest` testing framework file for xcorr predictor
"""

import pandas as pd
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
