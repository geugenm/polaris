"""
    Python module which will take matrix of params and list of transformers
    as input and outputs the list of best transformed values.
    Flattening the features distribution using entropy augmentation
"""
import ast
import csv
import re
from heapq import nlargest

import pandas as pd
import xgboost as xgb
from fets.pipeline import FeatureUnion2DF
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from polaris.learning.feature.selection import PARAMS

# List of time lags for the transformers
# _LAGS = ["0.25H", "0.5H", "1H", "3H", "6H", "12H", "24H"]


def get_time_lag(transf):
    """
        Utility function to get the time lag
        from the input transformer
    """
    transf = transf.replace('"', r'\"')
    length = len(transf)
    for index in range(length):
        if transf[index].isdigit():
            idx = index
            break
    return transf[idx:length - 3]


def build_transformer(feature):
    """
    Utility function to build the transformers from the previous
    most important features
    """
    split = feature.split("_")
    transformer = split[1] + '("' + split[2] + '")'
    col = split[0]
    return col, transformer, split[1]


def build_pipelines(transformers, data, original_features, prev_features):
    """
    Utility function to build pipelines using the transformers input
    and previous features
    """
    if prev_features:
        for prev in prev_features:
            print(prev)
            col, transformer, pipeline_id = build_transformer(prev)
            pipeline = Pipeline([("union",
                                  FeatureUnion2DF([
                                      (pipeline_id,
                                       ast.literal_eval(transformer))
                                  ]))])

            data[prev] = pipeline.transform(data[col])
    for _tf in transformers.split():
        integral = re.search(r'^TSIntegrale', _tf)
        scale = re.search(r'^TSScale', _tf)
        inter = re.search(r'^TSInterpolation', _tf)
        poly = re.search(r'^TSPolynomialAB', _tf)
        if integral.group(0) == 'TSIntegrale':
            pipeline_id = integral.group(0)
        elif scale.group(0) == 'TSScale':
            pipeline_id = scale.group(0)
        elif inter.group(0) == 'TSInterpolation':
            pipeline_id = inter.group(0)
        elif poly.group(0) == 'TSPolynomialAB':
            pipeline_id = poly.group(0)
        else:
            pipeline_id = ""
        pipeline = Pipeline([(pipeline_id, ast.literal_eval(_tf))])
        for col in original_features:
            data[col + "_" + pipeline_id + "_" +
                 get_time_lag(_tf)] = (pipeline.transform(data[col]))
    return data


def train_xgboostmodel(data):
    """
    Function to train the xgboost model.
    """
    model = xgb.XGBClassifier(**PARAMS)
    X = data.drop("NPWD2551", axis=1)
    Y = data.NPWD2551
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.33)
    del x_test
    del y_test
    model.fit(x_train, y_train)
    return model


def _get_feature_importances_for_xgboostmodel(data, original_features):
    """
    Utility function to get the list of top 10
    most important features.
    """
    model = train_xgboostmodel(data)
    augmented_features = data.drop(original_features, axis=1)
    importances = list(
        zip(augmented_features.columns, model.feature_importances_))
    importances.sort(key=lambda x: x[1], reverse=True)
    features = []
    importance = []
    for feat, imp in importances:
        features.append(feat)
        importance.append(imp)
    feature_importances = {
        features[i]: importance[i]
        for i in range(len(features))
    }
    top_feat = []
    top_imp = []
    ten_highest = nlargest(10,
                           feature_importances,
                           key=feature_importances.get)
    for fet in ten_highest:
        top_feat.append(fet)
        top_imp.append(feature_importances.get(fet))

    with open('/../topFeatures.csv', 'w') as _fl:
        writer = csv.writer(_fl)
        writer.writerows(zip(top_feat, top_imp))


def best_transformed_features(filepath, transformers, features_file):
    """
        Utility function to find out the
        best transformed features.
    """
    data_frame = pd.read_csv(filepath, index_col=[0])
    data_frame.index = pd.to_datetime(data_frame.index, unit='ms')
    data_frame = data_frame.loc['2014-01-01':'2014-02-01']
    previous_features = []
    try:
        with open(features_file) as fet:
            previous_features = [row.split(',')[0] for row in fet]
    except FileNotFoundError:
        print("No feature file provided")
    original_features = data_frame.columns
    data_frame = build_pipelines(transformers, data_frame, original_features,
                                 previous_features)
    _get_feature_importances_for_xgboostmodel(data_frame, original_features)
