"""
Module to launch different data analysis.
"""
from fets.math import TSIntegrale

from polaris.learning.feature.extraction import create_list_of_transformers, \
    extract_best_features


def feature_extraction(input_data, param):
    """
    Start feature extraction using the given settings.
    """
    # Create a small list of two transformers which will generate two
    # different pipelines
    transformers = create_list_of_transformers(["5min", "15min"], TSIntegrale)

    # Extract the best features of the two pipelines
    out = extract_best_features(input_data,
                                transformers,
                                target_column=param,
                                time_unit="ms")

    # out[0] is the FeatureImportanceOptimization object
    # from polaris.learning.feature.selection
    # pylint: disable=E1101
    print(out[0].best_features)
