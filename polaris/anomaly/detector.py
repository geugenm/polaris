"""Module to detect anomalies using an autoencoder
"""

import pandas as pd
from betsi.preprocessors import convert_from_column, convert_to_column, \
    normalize_all_data


def apply_preprocessing(data):
    """
    Function to apply preprocessing steps

    :param data: DataFrame which will undergo preprocessing
    :type data: pd.DataFrame
    :return: Tuple with the normalizer and converted data
    """

    window_size = 2
    stride = 1

    local_data = data.copy()

    normalized_data, normalizer = normalize_all_data(local_data)
    converted_data = convert_to_column(normalized_data, window_size, stride)

    return normalizer, converted_data


def remove_preprocessing(normalizer, data):
    """
    Function to remove preprocessing steps applied earlier

    :param normalizer: normalizer used to generate data in apply_preprocessing
    :param data: DataFrame to remove preprocessing from
    :type data: pd.DataFrame or np.array
    :return: Data with preprocessing removed
    :rtype: pd.DataFrame or np.array
    """

    window_size = 2
    stride = 1

    local_data = data.copy()

    converted_data = convert_from_column(local_data, window_size, stride)
    un_normalized_data = normalizer.inverse_transform(converted_data)

    if isinstance(data, pd.DataFrame):
        un_normalized_data = pd.DataFrame(un_normalized_data,
                                          columns=converted_data.columns)
    return un_normalized_data
