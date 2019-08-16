from collections import Iterable

import numpy as np
# import pandas as pd
import xgboost as xgb
from sklearn.base import BaseEstimator, TransformerMixin
# from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from fets.pipeline import FeatureUnion2DF


class FeatureImportanceOptimization(BaseEstimator, TransformerMixin):
    """
    Flattening the features' importances distribution using entropy
    augmentation (or distribution flattening).

    """

    def __init__(self, list_of_transformers):
        """ The constructor will help parameterize all options of this
        transformer

            :param list_of_transformers: list of externally built transformers
            objects in terms of scikit-learn pipeline compatible transformers.
            Meant to be a list of list of transformers to test different new
            features iteratively.

        """

        self.build_pipelines(list_of_transformers)

        # Each pipeline will have a corresponding model after fitting
        self.models = []
        # Model with optimized input
        self.model_optinput = None

        # Initial XGBoost parameters
        self.default_xgb_params = {
            'learning_rate': 0.1,
            'gamma': 0,
            'max_depth': 10,
            'n_estimators': 100,
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
        self.do_tuning = False

    def build_pipelines(self, list_of_transformers):
        """
            Create series of pipelines of transformers to be called to augment
            input datasets before searching for most important features.

            :param list_of_transformers: List (of list) of scikit-learn
            compatible transformers.
        """
        self.pipelines = []

        if list_of_transformers is None or list_of_transformers == []:
            return

        for transformer in list_of_transformers:
            # Preparing the list of transformer for one iteration
            tmp_pipeline = []
            if isinstance(transformer, Iterable):
                tmp_pipeline = [("T" + str(hash(k)), k)
                                for k in transformer
                                if issubclass(type(k), TransformerMixin)]
            elif issubclass(type(transformer), TransformerMixin):
                tmp_pipeline = [("T0", transformer)]

            # Creating the pipeline
            if len(tmp_pipeline) > 0:
                self.pipelines.append(
                    Pipeline([("union", FeatureUnion2DF(tmp_pipeline))]))

    def extract_feature_importance(self, columns, model):
        """ Extract a sorted list of feature importances from an XGBoost model

            :param columns: Columns names in the same order than the input
            dataset.
            :param model: A trained model containing feature importances list
            and trained trees.

        """
        importances = list(zip(columns, model.feature_importances_))
        importances.sort(key=lambda x: x[1], reverse=True)
        return importances

    def filter_importances(self, list_of_fimp, method="first_best"):
        """ Return a list of best features based on their importance

            **fimp** stands for Feature IMPortances.
            Each feature importance is expressed as a tuple (name, value)

            :param list_of_fimp: List of list of feature importances.  Each
            model would output a list of importances so this list is a list of
            all model's list of features importances.
            :param method: Method to filter best
            :return: Return a list of tuples ("feature_name",
            feature_importance) of the best features according to filtering
            `method`:
                - first_best method: select best of each feature list
                - all_best   method: select best features over all models
        """
        # wip: return  best features (for instance 10 or 5 highest)
        pass

    def importances_distribution_spread(self, importances):
        """ Calculated absolute average distance from perfectly flat
        distribution of importances.

            :param importances: list of tuples such as [(feature_name,
            feature_importance), (...), ...]

        """
        flat_score = 1.0
        nbr_of_importances = float(len(importances))
        if nbr_of_importances > 0.0:
            flat_score = 1.0 / nbr_of_importances
            return np.mean(np.abs([(flat_score - k[1]) for k in importances]))
        return flat_score

    def fit(self, input_x, input_y):
        """ Fit models for every pipeline and extract best features

            :param input_x: dataset (usually a dataframe) of features/predictor
            :param input_y: dataset (timseries or dataframe) of target(s) to
            predict.

        """

        # For now we take default hyperparameters
        xgboost_params = self.default_xgb_params

        # list of list of (tuples of) feature importances
        list_of_fimp = []

        for pipeline in self.pipelines:
            # Augment dataset with current pipeline
            input_dataset = pipeline.transform(input_x)
            # Train a model with augmented dataset
            self.models.append(xgb.XGBRegressor(**xgboost_params))
            self.models[-1].fit(input_dataset, input_y)

            # Extract feature importances and keep them for further analysis
            list_of_fimp.append(
                self.extract_feature_importance(self.models[-1]))

        # wip:
        return self

    def transform(self, input_data):
        """ Unused function here. Interface requirement.
        """
        return self
