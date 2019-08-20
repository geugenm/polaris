"""
This is a module to test extraction.py

"""
import unittest

import polaris.learning.feature.extraction as ext


class TestFeatureExtraction(unittest.TestCase):
    """
    Class for testing feature extraction.
    """

    def setUp(self):
        pass

    def _test_get_time_lags(self):
        self.assertEqual(ext.get_time_lag('TSIntegrale("30min")'), "30min")

    if __name__ == '__main__':
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
