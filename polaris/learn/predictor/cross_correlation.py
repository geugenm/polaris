"""
Cross Correlation module
"""

import logging
import warnings

import enlighten
import GPUtil
import numpy as np
import pandas as pd
# Used for tracking ML process results
from mlflow import log_metric, log_param, log_params, start_run
# Used for the pipeline interface of scikit learn
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV, KFold, train_test_split
# eXtreme Gradient Boost algorithm
from xgboost import XGBRegressor

from polaris.feature.cleaner import Cleaner

LOGGER = logging.getLogger(__name__)
warnings.simplefilter(action='ignore', category=FutureWarning)
# Remove this line when feature engineering is in place
np.seterr(divide='ignore', invalid='ignore')


class XCorr(BaseEstimator, TransformerMixin):
    """ Cross Correlation predictor class
    """
    def __init__(self,
                 model_params=None,
                 use_gridsearch=False,
                 xcorr_params=None,
                 force_cpu=False):
        """
            :param importances_map: dataframe representing the heatmap of corrs
            :param model_params: parameters for each model
            :param use_gridsearch: specify if gridsearch will be used during
            predictions
        """
        self.models = None
        self._importances_map = None
        self._feature_cleaner = Cleaner()
        self.xcorr_params = {
            "random_state": 42,
            "test_size": 0.2,
            "gridsearch_scoring": "neg_mean_squared_error",
            # The split number was obtained through trial-and-error,
            # it shoud be reviewed in the future to adapt to
            # the targeted satellite.
            "gridsearch_n_splits": 18
        }

        if use_gridsearch:
            self.method = self.gridsearch
            self.mlf_logging = self.gridsearch_mlf_logging
        else:
            self.method = self.regression
            self.mlf_logging = self.regression_mlf_logging

        self.model_params = set_model_params(model_params=model_params,
                                             force_cpu=force_cpu,
                                             use_gridsearch=use_gridsearch)

        if xcorr_params is not None:
            self.xcorr_params = xcorr_params

    @property
    def importances_map(self):
        """
        Return the importances_map value as Pandas Dataframe.

        """

        return self._importances_map

    @importances_map.setter
    def importances_map(self, importances_map):
        self._importances_map = importances_map

    def fit(self, X):
        """ Train on a dataframe

            The input dataframe will be split column by column considering each
            one as a prediction target.

            :param X: input dataframe
        """
        if not isinstance(X, pd.DataFrame):
            raise TypeError("Input data should be a DataFrame")

        if self.models is None:
            self.models = []

        self.reset_importance_map(X.columns)

        manager = enlighten.get_manager()
        # Preprocess the data
        LOGGER.info("Preprocessing Data. Removing unnecessary columns")
        X = self._feature_cleaner.handle_missing_values(X)

        pbar = manager.counter(total=X.shape[1],
                               desc="Columns",
                               unit="columns")

        with start_run(run_name='cross_correlate'):
            self.mlf_logging()
            for column in X.columns:
                LOGGER.info(column)
                try:
                    self.models.append(
                        self.method(X.drop([column], axis=1), X[column],
                                    self.model_params))
                except Exception as err:  # pylint: disable-msg=broad-except
                    if self.model_params.get("predictor") == "gpu_predictor":
                        LOGGER.info(" ".join([
                            "Encountered error using GPU.",
                            "Trying with CPU parameters now!"
                        ]))
                        self.model_params = {
                            "objective": "reg:squarederror",
                            "n_estimators": 80,
                            "learning_rate": 0.1,
                            "n_jobs": -1,
                            "predictor": "cpu_predictor",
                            "tree_method": "auto",
                            "max_depth": 8
                        }
                    else:
                        raise err
                pbar.update()

    def transform(self):
        """ Unused method in this predictor """
        return self

    def regression(self, df_in, target_series, model_params):
        """ Fit a model to predict target_series with df_in features/columns
            and retain the features importances in the dependency matrix.

            :param df_in: input dataframe representing the context, predictors.
            :param target_series: pandas series of the target variable. Share
            the same indexes as the df_in dataframe.
        """
        # Split df_in and target to train and test dataset
        df_in_train, df_in_test, target_train, target_test = train_test_split(
            df_in,
            target_series,
            test_size=0.2,
            random_state=self.xcorr_params['random_state'])

        # Create and train a XGBoost regressor
        regr_m = XGBRegressor(**model_params)
        regr_m.fit(df_in_train, target_train)

        # Make predictions
        target_series_predict = regr_m.predict(df_in_test)

        try:
            rmse = np.sqrt(
                mean_squared_error(target_test, target_series_predict))
            log_metric(target_series.name, rmse)
            LOGGER.info('Making predictions for : %s', target_series.name)
            LOGGER.info('Root Mean Square Error : %s', str(rmse))
        except Exception:  # pylint: disable-msg=broad-except
            # Because of large (close to infinite values) or nans
            LOGGER.error('Cannot find RMS Error for %s', target_series.name)
            LOGGER.debug('Expected %s, Predicted %s', str(target_test),
                         str(target_series_predict))

        # indices = np.argsort(regr_m.feature_importances_)[::-1]
        # After the model is trained
        new_row = {}
        for column, feat_imp in zip(df_in.columns,
                                    regr_m.feature_importances_):
            new_row[column] = [feat_imp]

        # Current target is not in df_in, so manually adding it
        new_row[target_series.name] = [0.0]

        # Sorting new_row to avoid concatenation warnings
        new_row = dict(sorted(new_row.items()))

        # Concatenating new information about feature importances
        if self._importances_map is not None:
            self._importances_map = pd.concat([
                self._importances_map,
                pd.DataFrame(index=[target_series.name], data=new_row)
            ])
        return regr_m

    def gridsearch(self, df_in, target_series, params):
        """ Apply gridchear to fine-tune XGBoost hyperparameters
            and then call the regression method based on the results.

            :param df_in: input dataframe representing the context, predictors.
            :param target_series: pandas series of the target variable. Share
            the same indexes as the df_in dataframe.
            :param params: the hyperparameters to use on the gridsearch
            method.
        """
        if not isinstance(df_in, pd.DataFrame):
            LOGGER.error("Expected %s got %s for df_in in gridsearch",
                         pd.DataFrame, type(df_in))
            raise TypeError

        random_state = self.xcorr_params['random_state']
        kfolds = KFold(n_splits=self.xcorr_params['gridsearch_n_splits'],
                       shuffle=True,
                       random_state=random_state)
        regr_m = XGBRegressor(random_state=random_state,
                              predictor="cpu_predictor",
                              tree_method="auto",
                              n_jobs=-1)

        gs_regr = GridSearchCV(regr_m,
                               param_grid=params,
                               cv=kfolds,
                               scoring=self.xcorr_params['gridsearch_scoring'],
                               verbose=1)
        gs_regr.fit(df_in, target_series)

        log_param(target_series.name + ' best estimator', gs_regr.best_params_)
        LOGGER.info("%s best estimator : %s", target_series.name,
                    str(gs_regr.best_estimator_))
        return self.regression(df_in, target_series, gs_regr.best_params_)

    def reset_importance_map(self, columns):
        """
        Creating an empty importance map
        """
        if self._importances_map is None:
            self._importances_map = pd.DataFrame(data={}, columns=columns)

    def common_mlf_logging(self):
        """ Log the parameters used for gridsearch and regression
            in mlflow
        """
        log_param('Test size', self.xcorr_params['test_size'])
        log_param('Model', 'XGBRegressor')

    def gridsearch_mlf_logging(self):
        """ Log the parameters used for gridsearch
            in mlflow
        """
        log_param('Gridsearch scoring',
                  self.xcorr_params['gridsearch_scoring'])
        log_param('Gridsearch parameters', self.model_params)
        self.common_mlf_logging()

    def regression_mlf_logging(self):
        """ Log the parameters used for regression
            in mlflow.
        """
        self.common_mlf_logging()
        log_params(self.model_params)


# pylint: disable-msg=too-many-branches
def set_model_params(model_params=None, force_cpu=False, use_gridsearch=False):
    """Sets model params

    :param model_params: Custom parameters (user specified)
    :param force_cpu: If True, doesn't check GPU availability
    :param use_gridsearch: If models are for gridsearch
    """
    if model_params is not None:
        LOGGER.info(" ".join(["Using custom model parameters!"]))
        if not isinstance(model_params, dict):
            raise TypeError("Expected {} got {}".format(
                dict, type(model_params)))

        if use_gridsearch:
            for param in model_params.keys():
                if not isinstance(model_params[param], list):
                    raise TypeError("Expected {} got {} for key {}".format(
                        list, type(model_params[param]), param))

        return model_params

    if use_gridsearch:
        LOGGER.info(" ".join(["Using gridsearch parameters!"]))
        model_params = {
            "objective": ["reg:squarederror"],
            "n_estimators": [50, 100, 300],
            "learning_rate": [0.005, 0.05, 0.1, 0.2],
            "max_depth": [3, 5, 8, 15],
        }

    else:
        LOGGER.info(" ".join(["Plain old gridsearch parameters!"]))
        model_params = {
            "objective": "reg:squarederror",
            "n_estimators": 80,
            "learning_rate": 0.1,
            "n_jobs": -1,
            "max_depth": 8
        }

    if not force_cpu:
        try:
            gpu_ids = GPUtil.getAvailable()
        except ValueError:
            # As reported at
            # https://github.com/anderskm/gputil/issues/26, GPUtil
            # will throw ValueError if NVidia hardware is detected,
            # but the driver is not loaded.  This is not terribly
            # helpful.  As a workaround, we'll set the list of gpus to
            # [].
            LOGGER.warning("".join([
                "GPU requested but not detected.",
                "Are you sure you have the proper drivers installed?"
            ]))
            gpu_ids = []

        if gpu_ids != []:
            LOGGER.info(" ".join(["GPU detected! Adding GPU parameters :)"]))

            # For the params chosen, refer:
            # https://xgboost.readthedocs.io/en/latest/gpu/
            if use_gridsearch:
                model_params['tree_method'] = ['gpu_hist']
                model_params['predictor'] = ['gpu_predictor']
                model_params['gpu_id'] = [gpu_ids[0]]
            else:
                model_params['tree_method'] = 'gpu_hist'
                model_params['predictor'] = 'gpu_predictor'
                model_params['gpu_id'] = gpu_ids[0]
            return model_params

    LOGGER.info(" ".join(["No GPU detected! Adding CPU parameters :)"]))
    if use_gridsearch:
        model_params['tree_method'] = ['approx']
        model_params['predictor'] = ['cpu_predictor']
        model_params['n_jobs'] = [-1]
    else:
        model_params['tree_method'] = 'approx'
        model_params['predictor'] = 'cpu_predictor'
        model_params['n_jobs'] = -1
    return model_params
