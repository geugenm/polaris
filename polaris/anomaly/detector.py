"""Module to detect anomalies using an autoencoder
"""
import logging

import pandas as pd
from betsi.models import custom_autoencoder
from betsi.preprocessors import convert_from_column, convert_to_column, \
    normalize_all_data
from sklearn.model_selection import train_test_split

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
        ae_model, en_model, de_model = create_models(layer_dims, activations)
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
    ae_model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
    en_model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
    de_model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

    return (ae_model, en_model, de_model)


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

    (ae_model, en_model, de_model) = models

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
        history = ae_model.fit(train_data,
                               train_data,
                               batch_size=batch_size,
                               epochs=epochs)
    except Exception as err:
        # Exception if data not formatted properly, gradients vanishing
        # or some model errors
        LOGGER.error("Error fitting data. Aborting anomaly detection")
        raise err

    # Get the results on test data to verify model has not overfit
    test_results = ae_model.evaluate(test_data,
                                     test_data,
                                     batch_size=batch_size)
    LOGGER.info("Test loss: %s, Test MSE: %s", str(test_results[0]),
                str(test_results[1]))

    models = (ae_model, en_model, de_model)
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
