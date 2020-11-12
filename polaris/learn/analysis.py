"""
Module to launch different data analysis.
"""
import logging

from fets.math import TSIntegrale
from mlflow import set_experiment

from polaris.data.graph import PolarisGraph
from polaris.data.readers import read_polaris_data
from polaris.dataset.metadata import PolarisMetadata
from polaris.learn.feature.extraction import create_list_of_transformers, \
    extract_best_features
from polaris.learn.predictor.cross_correlation import XCorr
from polaris.learn.predictor.cross_correlation_configurator import \
    CrossCorrelationConfigurator

LOGGER = logging.getLogger(__name__)


class NoFramesInInputFile(Exception):
    """Raised when frames dataframe is empty"""


def feature_extraction(input_file, param_col):
    """
    Start feature extraction using the given settings.

        :param input_file: File path to input data (dataframe csv)
        :param param_col: Target column
    """
    # Create a small list of two transformers which will generate two
    # different pipelines
    transformers = create_list_of_transformers(["5min", "15min"], TSIntegrale)

    # Extract the best features of the two pipelines
    out = extract_best_features(input_file,
                                transformers,
                                target_column=param_col,
                                time_unit="ms")

    # out[0] is the FeatureImportanceOptimization object
    # from polaris.learn.feature.selection
    # pylint: disable=E1101
    print(out[0].best_features)


# pylint: disable-msg=too-many-arguments
def cross_correlate(input_file,
                    output_graph_file=None,
                    xcorr_configuration_file=None,
                    graph_link_threshold=0.1,
                    use_gridsearch=False,
                    csv_sep=',',
                    force_cpu=False):
    """
    Catch linear and non-linear correlations between all columns of the
    input data.

        :param model_params: XGBoost parameters dictionary
    """
    # Reading input file - index is considered on first column
    metadata, dataframe = read_polaris_data(input_file, csv_sep)

    if dataframe.empty:
        LOGGER.error("Empty list of frames -- nothing to learn from!")
        raise NoFramesInInputFile

    input_data = normalize_dataframe(dataframe)
    source = metadata['satellite_name']

    set_experiment(experiment_name=source)

    xcorr_configurator = CrossCorrelationConfigurator(
        xcorr_configuration_file=xcorr_configuration_file,
        use_gridsearch=use_gridsearch,
        force_cpu=force_cpu)

    # Creating and fitting cross-correlator
    xcorr = XCorr(metadata, xcorr_configurator.get_configuration())
    xcorr.fit(input_data)

    if output_graph_file is None:
        output_graph_file = "/tmp/polaris_graph.json"

    metadata = PolarisMetadata({"satellite_name": source})
    graph = PolarisGraph(metadata=metadata)
    graph.from_heatmap(xcorr.importances_map, graph_link_threshold)
    with open(output_graph_file, 'w') as graph_file:
        graph_file.write(graph.to_json())


def normalize_dataframe(dataframe):
    """
        Apply dataframe modification for being used
        by the learn module.

        :param dataframe: the pandas dataframe to normalize
        :return: Pandas dataframe normalized
    """
    dataframe.index = dataframe.time
    dataframe.drop(['time'], axis=1, inplace=True)

    return dataframe
