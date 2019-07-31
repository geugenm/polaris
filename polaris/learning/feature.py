"""Utility function which will take matrix of params and list of transformers
as input and outputs the list of best transformed values.
Flattening the features distribution using entropy augmentation"""

import json
import re
from datetime import datetime

import numpy as np
import pandas as pd
import xgboost as xgb
# import fets
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

params = {
    'learning_rate': 0.1,
    'gamma': 0,
    'max_depth': 10,
    'n_estimators': 50,
    'base_score': 0.5,
    'colsample_bylevel': 1,
    'colsample_bytree': 1,
    'max_delta_step': 0,
    'min_child_weight': 1,
    'missing': None,
    'nthread': 100,
    'objective': "reg:linear",
    'reg_alpha': 0,
    'reg_lambda': 1,
    'scale_pos_weight': 1,
    'seed': 0,
    'verbosity': 1,
    'subsample': 1,
    'predictor': "gpu_predictor",
    'tree_method': "auto"
}


def _maxdist(x_i, x_j):
    return max([abs(ua - va) for ua, va in zip(x_i, x_j)])


"""Utility function to calculate the sample entropy which is
similar to approximate entropy but it is more consistent in
estimating the complexity even for small time series"""


def sample_entropy(timeseries_data, run_data_length, filtering_level):
    def _phi(run_data_length):
        x = [[
            timeseries_data[j] for j in range(i, i + run_data_length - 1 + 1)
        ] for i in range(N - run_data_length + 1)]
        C = [
            len([
                1 for j in range(len(x))
                if i != j and _maxdist(x[i], x[j]) <= filtering_level
            ]) for i in range(len(x))
        ]
        return sum(C)

    N = len(timeseries_data)
    return -np.log(_phi(run_data_length + 1) / _phi(run_data_length))


"""Utility function to calculate the approximate entropy which quantify the
regularity and unpredictability of the fluctuations in time series data."""


def approximate_entropy(timeseries_data, run_data_length, filtering_level):
    def _phi(run_data_length):
        x = [[
            timeseries_data[j] for j in range(i, i + run_data_length - 1 + 1)
        ] for i in range(N - run_data_length + 1)]
        C = [
            len([1 for x_j in x if _maxdist(x_i, x_j) <= filtering_level]) /
            (N - run_data_length + 1.0) for x_i in x
        ]
        return (N - run_data_length + 1.0)**(-1) * sum(np.log(C))

    N = len(timeseries_data)
    return abs(_phi(run_data_length + 1) - _phi(run_data_length))


# List of time lags for the transformers
# _LAGS = ["0.25H", "0.5H", "1H", "3H", "6H", "12H", "24H"]


def get_time_lag(tf):
    tf = tf.replace('"', r'\"')
    length = len(tf)
    for i in range(length):
        if (tf[i].isdigit()):
            idx = i
            break
    return tf[idx:length - 3]


def build_transformer(feature):
    split = feature.split("_")
    print
    transformer = split[1] + '("' + split[2] + '")'
    print(transformer)
    col = split[0]
    return col, transformer, split[1]


""" Utility function to build pipelines using the transformers input and the
_LAGS list"""


def build_pipelines(transformers, data, original_features, prev_features):
    for prev in prev_features:
        col, transformer, pipeline_id = build_transformer(prev)
        pipeline = Pipeline([pipeline_id, transformer])
        data[prev] = pipeline.transform(data[col])
    for tf in transformers:
        integral = re.search('^TSIntegrale', tf)
        scale = re.search('^TSScale', tf)
        inter = re.search('^TSInterpolation', tf)
        poly = re.search('^TSPolynomialAB', tf)
        if integral:
            pipeline_id = "TSIntegrale"
        if scale:
            pipeline_id = "TSScale"
        if inter:
            pipeline_id = "TSInterpolation"
        if poly:
            pipeline_id = "TSPolynomial"
        else:
            pipeline_id = ""


#     for lag in _LAGS:
#       steps = tf+"("+lag+")"

    pipeline = Pipeline([pipeline_id, tf])
    for col in original_features:
        data[col + "_" + pipeline_id + "_" +
             get_time_lag(tf)] = (pipeline.transform(data[col]))
    return data


def get_feature_importances_for_xgboostModel(data, original_features):
    model = xgb.XGBClassifier(**params)
    X = data.NPWD2551
    Y = data.drop(data.NPWD2551)
    X_train, x_test, Y_train, y_test = train_test_split(X, Y, test_size=0.33)
    model.fit(X_train, Y_train)
    importances = list(zip(data.columns, model.feature_importances_))
    importances.sort(key=lambda x: x[1], reverse=True)
    features = []
    importances = []
    for F, I in importances:
        print("{}: {}".format(F, I))
        if F not in original_features:
            features.append(F)
            importances.append(I)
        else:
            continue
    feature_importances = dict(zip(features, importances))
    jsonf = json.dumps(feature_importances)
    f = open("feature_importances.json", "w")
    f.write(jsonf)
    f.close()


def best_transformed_features(filepath,
                              transformers,
                              features_file="",
                              start_date='2014-01-01',
                              end_date='2014-02-01'):
    data = pd.read_csv(filepath, index=[0])
    data.index = pd.to_datetime(data.index, unit='ms')
    start_date = datetime(start_date)
    end_date = datetime(end_date)
    data = data.loc[start_date:end_date]
    if features_file:
        try:
            with open(features_file) as handle:
                dictdump = json.loads(handle.read())
            prev_features = list(dictdump)
        except Exception:
            print("No feature file provided")
    original_features = data.columns
    data = build_pipelines(transformers, data, original_features,
                           prev_features.keys())
