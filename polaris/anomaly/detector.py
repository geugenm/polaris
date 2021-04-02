"""Module to detect anomalies using an autoencoder
"""
import json
import logging
import os

import joblib
import pandas as pd
from betsi.models import custom_autoencoder
from betsi.predictors import distance_measure, get_events
from betsi.preprocessors import convert_from_column, convert_to_column, \
    normalize_all_data
from sklearn.model_selection import train_test_split

from polaris.data import readers
from polaris.feature.cleaner import Cleaner
from polaris.feature.cleaner_configurator import CleanerConfigurator

LOGGER = logging.getLogger(__name__)


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


def create_models(layer_dims, activations=None):
    """Creates the 3 models: autoencoder, encoder and decoder

    :param layer_dims: list containing the dimensions of the layers (till the
        bottleneck layer)
    :type layer_dims: list
    :param activations: list of activations for each layer, defaults to None
    :type activations: list, optional
    :raises ValueError: If the model could not be created
    :return: tuple containing the (autoencoder, encoder, decoder) models
    :rtype: tuple
    """
    try:
        return custom_autoencoder(layer_dims, activations)

    except ValueError as err:
        LOGGER.error("Error creating the model. This might be because:")
        LOGGER.error("1. Layer dimensions are incorrect")
        LOGGER.error("2. Activation specified does not exist")
        raise err


def create_compile_model(layer_dims, activations=None):
    """Function to create and compile the model

    :param layer_dims: list containing the dimensions of the layers (till the
        bottleneck layer)
    :type layer_dims: list
    :param activations: list of activations for each layer, defaults to None
    :type activations: list, optional
    :return: tuple containing the (autoencoder, encoder, decoder) models
    :rtype: tuple
    """
    optimizer = "adam"
    loss = "mean_squared_error"
    metrics = ["MSE"]

    try:
        # Try creating the model using betsi
        autoencoder_model, encoder_model, decoder_model = create_models(
            layer_dims, activations)
    except ValueError as err:
        # Error might occur if the activations are malformed or the layer
        # sizes are incorrect
        LOGGER.error(
            "Error creating models."
            " Layer sizes are %s, activations are %s", str(layer_dims),
            str(activations))
        # Raising error from err to get the whole traceback
        raise ValueError from err

    # Compiling the autoencoder model
    autoencoder_model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
    encoder_model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
    decoder_model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

    return (autoencoder_model, encoder_model, decoder_model)


def train_test_model(preprocessed_data, models):
    """Function to train and test the compiled model

    :param preprocessed_data: DataFrame with preprocessed data
    :type preprocessed_data: pd.DataFrame
    :param models: Tuple containing autoencoder, encoder and decoder models
    :type models: tuple
    :return: Tuple containing trained models, training history and train-test
        data
    :rtype: tuple
    """
    test_size = 0.33
    batch_size = 128
    epochs = 20

    (autoencoder_model, encoder_model, decoder_model) = models

    # Split it into train and test data, set shuffle to false as order matters
    # since it is time series data
    train_data, test_data = train_test_split(preprocessed_data,
                                             test_size=test_size,
                                             shuffle=False)

    # Train the model for epochs number of epochs, keep history for
    # further analysis
    LOGGER.info("Training on %i rows of data, with batch size %i and epoch %i",
                train_data.shape[0], batch_size, epochs)
    try:
        history = autoencoder_model.fit(train_data,
                                        train_data,
                                        batch_size=batch_size,
                                        epochs=epochs)
    except Exception as err:
        # Exception if data not formatted properly, gradients vanishing
        # or some model errors
        LOGGER.error("Error fitting data. Aborting anomaly detection")
        raise err

    # Get the results on test data to verify model has not overfit
    test_results = autoencoder_model.evaluate(test_data,
                                              test_data,
                                              batch_size=batch_size)
    LOGGER.info("Test loss: %s, Test MSE: %s", str(test_results[0]),
                str(test_results[1]))

    models = (autoencoder_model, encoder_model, decoder_model)
    data = (train_data, test_data)

    return models, history, data


def preprocess_train_model(data, layer_dims, activations=None):
    """Function to preprocess data, create and train models

    :param data: DataFrame with data to train on
    :type data: pd.DataFrame
    :param layer_dims: List containing dimension of all layers till bottleneck
        layer except input layer (which will be calculated)
    :type layer_dims: list
    :param activations: List of activation functions for each layer. Should be
        valid keras activation function, defaults to None
    :type activations: list, optional
    :return: Tuple with normalizer, trained models and training history
    :rtype: tuple
    """

    # Preprocess the data
    LOGGER.info("Preprocessing data")
    normalizer, preprocessed_data = apply_preprocessing(data)
    layer_dims = [preprocessed_data.shape[1]] + layer_dims

    # Create and compile the models
    LOGGER.info("Creating and compiling models")
    models = create_compile_model(layer_dims, activations)

    LOGGER.info("Training and testing models")
    models, history, tt_data = train_test_model(preprocessed_data, models)

    # Returning the test and train data as it is required for predictions
    return normalizer, models, history, tt_data


def save_all(cache_dir, models, tt_data, normalizer, anomaly_metrics):
    """Save all important variables in files

    :param cache_dir: Path to cache directory
    :param models: tuple with autoencoder_model, encoder_model, decoder_model
    :param tt_data: train and test dataframes (list)
    :param normalizer: Normalizer used while creating the data
    :param anomaly_metrics: Dictionary containing other metrics
    """
    if not os.path.isdir(cache_dir):
        try:
            os.makedirs(cache_dir)
        except Exception as err:
            LOGGER.error(
                "Error creating the path %s."
                "Do you have the correct permissions?", str(cache_dir))
            raise err

    autoencoder_model, encoder_model, decoder_model = models

    # Save models to respective files
    autoencoder_model.save(
        os.path.join(cache_dir, "autoencoder_model.tf_model"))
    encoder_model.save(os.path.join(cache_dir, "encoder_model.tf_model"))
    decoder_model.save(os.path.join(cache_dir, "decoder_model.tf_model"))

    # Save test and train data for future use (while visualizing)
    tt_data[0].to_pickle(os.path.join(cache_dir, "train_data.pkl"))
    tt_data[1].to_pickle(os.path.join(cache_dir, "test_data.pkl"))

    # Save the normalizer to preprocess data next time
    joblib.dump(normalizer, os.path.join(cache_dir, "normalizer.pkl"))

    # Save all the anomaly metrics (training history, events)
    with open(os.path.join(cache_dir, "anomaly_metrics.json"),
              "w") as json_file:
        json.dump(anomaly_metrics, json_file)


def detect_events(df_pred_bn, noise_margin_per):
    """Function to detect anomalies/events

    :param df_pred_bn: bottleneck layer prediction
    :param noise_margin_per: percentage above average distance_sum the value
        needs to be for detection as peak
    :return: list of event indices
    :rtype: list
    """
    # Get distances
    distance_list = []
    for row_no in range(df_pred_bn.shape[0] - 1):
        distance_list.append(
            distance_measure(df_pred_bn[row_no], df_pred_bn[row_no + 1]))

    events = get_events(distance_list, threshold=noise_margin_per)

    return events


# Disabling because there are 16 instead of 15 vars. Once we switch to
# configurator, remove this
# pylint: disable=too-many-locals
def train_predict_store(import_file, cache_dir, layer_dims):
    """Train, predict and store models

    :param import_file: Valid file generated by polaris.fetch
    :type import_file: os.path/os.path
    :param cache_dir: Directory where cached data are store
    :type cache_dir: os.path/str
    :param layer_dims: List of layer dimensions
    :type layer_dims: list
    """
    # For config file
    noise_margin_per = 150
    clean_params = CleanerConfigurator()

    # Read data from import file
    metadata, data = readers.read_polaris_data(import_file)
    feature_cleaner = Cleaner(metadata, clean_params.get_configuration())
    data = feature_cleaner.drop_constant_values(data)
    data = feature_cleaner.drop_non_numeric_values(data)
    data = feature_cleaner.handle_missing_values(data)
    data = data.select_dtypes("number")

    # Complete training
    normalizer, models, history, tt_data = preprocess_train_model(
        data, layer_dims)

    encoder_model = models[1]

    # Get the bottleneck prediction
    df_pred_bn = encoder_model.predict(tt_data[1])

    events = detect_events(df_pred_bn, noise_margin_per)

    anomaly_metrics = {
        "history": history.history,
        "events": events,
    }

    save_all(cache_dir, models, tt_data, normalizer, anomaly_metrics)
