"""
`pytest` testing framework file for xcorr predictor
"""

import itertools

import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from polaris.learn.predictor.cross_correlation import XCorr, set_model_params


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


@pytest.mark.parametrize("use_gridsearch, force_cpu, use_sample_model_params",
                         list(itertools.product((True, False), repeat=3)))
def test_set_model_params_no_exception(use_gridsearch, force_cpu,
                                       use_sample_model_params):
    """
    Test for set_model_params when no exception occurs
    """
    if use_sample_model_params:
        if not use_gridsearch:
            model_params_good = {
                "objective": "reg:squarederror",
                "n_estimators": 80,
            }

        else:
            model_params_good = {
                "objective": ["reg:squarederror"],
                "n_estimators": [80],
            }

        _ = set_model_params(model_params=model_params_good,
                             force_cpu=force_cpu,
                             use_gridsearch=use_gridsearch)

    else:
        _ = set_model_params(force_cpu=force_cpu,
                             use_gridsearch=use_gridsearch)


@pytest.mark.parametrize("use_gridsearch, force_cpu, use_sample_model_params",
                         list(itertools.product((True, False), repeat=3)))
def test_set_model_params_exception(use_gridsearch, force_cpu,
                                    use_sample_model_params):
    """
    Test for set_model_params when exception occurs
    """
    if use_sample_model_params:
        model_params_bad = [[1, 2, 'this is bad']]

        if use_gridsearch:
            model_params_bad.append({
                "objective": "reg:squarederror",
                "n_estimators": 80,
            })

        for model_params in model_params_bad:
            with pytest.raises(TypeError):
                _ = set_model_params(model_params=model_params,
                                     force_cpu=force_cpu,
                                     use_gridsearch=use_gridsearch)
