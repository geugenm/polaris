"""
`pytest` testing framework file for xcorr predictor
"""

import os
import sys
import pandas as pd
from sklearn.pipeline import Pipeline
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from polaris.learning.predictor.cross_correlation import XCorr


def test_xcorr():
    """
    `pytest` entry point
    """

    test_df = pd.DataFrame({
        "A":[4, 123, 24.2, 3.14, 1.41],
        "B":[7,   0, 24.2, 3.14, 8.2]
        })
    A = XCorr()
    assert A.importances_map is None

    A.fit(test_df)
    assert A.importances_map is not None
    assert isinstance(A.importances_map, pd.DataFrame)
    assert A.importances_map.shape[0] == 2
    assert A.importances_map.shape[1] == A.importances_map.shape[0]
    

def test_xcorr_pipeline():
    """
    `pytest` entry point
    """

    pipeline = Pipeline([
        ("deps", XCorr())
    ])

    assert pipeline is not None
