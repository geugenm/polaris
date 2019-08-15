from unittest import TestCase

from polaris.learning.feature.selection import FeatureImportanceOptimization


class Transformers(object):
    def set_transformers(self):
        list_of_transformers = ['TSIntegrale("3H")', 'TSIntegrale("30min")']
        return list_of_transformers


class FeatureImportanceOptimizationTest(TestCase):
    def setUp(self):
        self.fio = FeatureImportanceOptimization(Transformers())
        self.assertEqual(0, len(self.fio.models))
        self.assert self.fio.model_optinput is None
        self.assert self.fio.do_tuning is False

    def test_build_pipelines(self):
        self.assertEqual(0, len(self.fio.pipelines))
        self.fio.build_pipelines(Transformers())
