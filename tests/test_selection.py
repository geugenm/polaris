from unittest import TestCase

from polaris.learning.feature.selection import FeatureImportanceOptimization


class Transformers(object):
    def set_transformers(self):
        list_of_transformers = ['TSIntegrale("3H")', 'TSIntegrale("30min")']
        return list_of_transformers


class FeatureImportanceOptimizationTest(TestCase):
    def setUp(self):
        self.fio = FeatureImportanceOptimization(Transformers())

    def test_build_pipelines(self):
        self.assertEqual(0, self.fio.pipelines.length)
        self.fio.build_pipelines(Transformers())
