import unittest

import polaris.learning.feature.extraction as ext


class test_feature_extraction(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_time_lags(self):
        self.assertEqual(ext.get_time_lag('TSIntegrale("30min")'), "30min")

    if __name__ == '__main__':
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
