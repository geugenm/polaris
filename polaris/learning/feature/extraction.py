"""Utility function which will take matrix of params and list of transformers
as input and outputs the list of best transformed values.
Flattening the features distribution using entropy augmentation"""

import csv
import re
from heapq import nlargest

import pandas as pd
import xgboost as xgb
# from fets.math import *
from fets.pipeline import FeatureUnion2DF
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


""" Utility function to build the transformers from the previous
    most important features"""


def build_transformer(feature):
    split = feature.split("_")
    transformer = split[1] + '("' + split[2] + '")'
    col = split[0]
    return col, transformer, split[1]


""" Utility function to build pipelines using the transformers input
and previous features"""


def build_pipelines(transformers, data, original_features, prev_features):
    if len(prev_features) > 0:
        for prev in prev_features:
            print(prev)
            col, transformer, pipeline_id = build_transformer(prev)
            pipeline = Pipeline(
                              [("union", FeatureUnion2DF(
                                [
                                  (pipeline_id, eval(transformer))
                                ]
                                ))
                               ]
                            )

            data[prev] = pipeline.transform(data[col])
    for tf in transformers.split():
        integral = re.search(r'^TSIntegrale', tf)
        scale = re.search(r'^TSScale', tf)
        inter = re.search(r'^TSInterpolation', tf)
        poly = re.search(r'^TSPolynomialAB', tf)
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
        pipeline = Pipeline([(pipeline_id, eval(tf))])
        for col in original_features:
            data[col + "_" + pipeline_id + "_" +
                 get_time_lag(tf)] = (pipeline.transform(data[col]))
    return data


def get_feature_importances_for_xgboostModel(data, original_features):
    model = xgb.XGBClassifier(**params)
    X = data.drop("NPWD2551", axis=1)
    Y = data.NPWD2551
    X_train, x_test, Y_train, y_test = train_test_split(X, Y, test_size=0.33)
    model.fit(X_train, Y_train)
    augmented_features = data.drop(original_features, axis=1)
    importances = list(
        zip(augmented_features.columns, model.feature_importances_))
    importances.sort(key=lambda x: x[1], reverse=True)
    features = []
    importance = []
    for F, I in importances:
        features.append(F)
        importance.append(I)
    feature_importances = {
        features[i]: importance[i]
        for i in range(len(features))
    }
    topFeat = []
    topImp = []
    tenHighest = nlargest(10, feature_importances, key=feature_importances.get)
    for f in tenHighest:
        topFeat.append(f)
        topImp.append(feature_importances.get(f))

    with open('/../topFeatures.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(zip(topFeat, topImp))


def best_transformed_features(filepath, transformers, features_file):
    df = pd.read_csv(filepath, index_col=[0])
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.loc['2014-01-01':'2014-02-01']
    previous_features = []
    try:
        with open(features_file) as f:
            previous_features = [row.split(',')[0] for row in f]
    except Exception:
        print("No feature file provided")
    original_features = df.columns
    df = build_pipelines(transformers, df, original_features,
                         previous_features)
    get_feature_importances_for_xgboostModel(df, original_features)
