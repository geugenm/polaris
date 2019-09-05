"""
Module for testing selection.py script.
"""
import pytest
from fets.math import TSIntegrale

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


@pytest.mark.parametrize("list_of_imp, result", [(None, None),
                                                 ([("a", 0.093281),
                                                   ("b", 0.069863),
                                                   ("c", 0.05984),
                                                   ("d", 0.05914),
                                                   ("e", 0.053266),
                                                   ("f", 0.01), ("g", 0.05198),
                                                   ("h", 0.05093),
                                                   ("i", 0.046125),
                                                   ("j", 0.0410098)], 4)])
def test_find_gap(list_of_imp, result):
    """ Test of finding a gap in the feature importances

        :param list_of_imp: list of feature importances
    """
    fimp_op = FeatureImportanceOptimization(list_of_imp)
    assert fimp_op.find_gap(list_of_imp) == result


@pytest.fixture(name="input_transformers")
def fixture_input_transformers():
    """ Creating a fixed set of transformers """
    transformers_list = [TSIntegrale("3H"), TSIntegrale("12H")]
    return transformers_list


def test_build_pipelines(input_transformers):
    """ Testing the function build_pipelines on the argument
        list of transformers.

        :param input_transformers: fixtures for input transformers
    """
    fio = FeatureImportanceOptimization(input_transformers)
    assert len(fio.pipelines) == 2
    # Checking if pipelines are reset
    fio.build_pipelines(input_transformers)
    assert len(fio.pipelines) == 2
