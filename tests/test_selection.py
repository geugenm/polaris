"""
Module for testing selection.py script.
"""
from fets.math import TSIntegrale

import pytest
from polaris.learning.feature.selection import FeatureImportanceOptimization


@pytest.mark.parametrize("list_of_transformers,exp_pipes", [
    (None, 0),
    ([], 0),
    (["FAKE"], 0),
    (["FAKE", "NOT_A_TRANSFORMER"], 0),
    ([TSIntegrale("30min")], 1),
    ([(TSIntegrale("5min"), TSIntegrale("30min"))], 1),
    ([(TSIntegrale("5min"), TSIntegrale("30min")),
      TSIntegrale("15min")], 2),
])
def test_fio_init(list_of_transformers, exp_pipes):
    """ Testing the initalization of FeatureImportanceOptimization objects

        :param list_of_transformers: different list of transformers
        :param exp_pipes: Expected number of pipelines
    """
    fio = FeatureImportanceOptimization(list_of_transformers)
    assert len(fio.pipelines) == exp_pipes
    assert fio.do_tuning is False
    assert fio.model_optinput is None


@pytest.mark.parametrize("list_of_fimp, method, result", [
    (None, "first_best", []),
    ([[("a", 0.2), ("b", 0.8)]], "first_best", [("b", 0.8)]),
])
def test_filter_importances(list_of_fimp, method, result):
    """ Test of the importance filtering

        :param list_of_fimp: list of lists of feature importances
        :param method: method for filtering
    """
    fimp_op = FeatureImportanceOptimization([TSIntegrale("30min")])
    selected_features = fimp_op.filter_importances(list_of_fimp, method)
    assert selected_features == result
