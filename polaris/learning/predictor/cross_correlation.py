import pandas as pd

# eXtreme Gradient Boost algorithm
from xgboost import XGBRegressor

# Used for the pipeline interface of scikit learn
from sklearn.base import BaseEstimator, TransformerMixin


class XCorr(BaseEstimator, TransformerMixin):
    """ Cross Correlation predictor class
    """

    def __init__(self, model_params=None):
        """
            :param models: list of tuples (target column, model)
            :param importances_map: dataframe representing the heatmap of correlations
            :param model_params: parameters for each model
        """
        self.models = None
        self.importances_map = None
        self.early_stopping_rounds = 5

        # Model parameters in use for all iterations
        # These parameters could be optimized with
        # with a search method, such as the grid search.
        self.model_params = {
            "objective": "reg:linear",
            "n_estimators": 80,
            "learning_rate": 0.1,
            "n_jobs": -1,
            # "max_depth": 8
        }
        if model_params is not None:
            self.model_params = model_params

    def fit(self, X):
        """ Train on a dataframe

            The input dataframe will be split column by column considering each
            one as a prediction target.

            :param X: input dataframe
        """
        if not isinstance(X, pd.DataFrame):
            raise TypeError("Input X should be a DataFrame")

        if self.models is None:
            self.models = []

        self.reset_importance_map(X.columns)

        for c in X.columns:
            self.models.append(
                self.regression(X.drop([c], axis=1), X[c])
            )

    def transform(self):
        """ Unused method in this predictor """
        return self

    def regression(self, df_in, target_series):
        """ Fit a model to predict target_series with df_in features/columns
            and retain the features importances in the dependency matrix.

            :param df_in: input dataframe representing the context, predictors.
            :param target_series: pandas series of the target variable. Share
            the same indexes as the df_in dataframe.
        """
        # Create and train a XGBoost regressor
        M = XGBRegressor(**self.model_params)
        # , early_stopping_rounds=self.early_stopping_rounds)
        M.fit(df_in, target_series)

        # indices = np.argsort(M.feature_importances_)[::-1]
        # After the model is trained
        new_row = {}
        for c, fi in zip(df_in.columns, M.feature_importances_):
            new_row[c] = [fi]

        # Current target is not in df_in, so manually adding it
        new_row[target_series.name] = [0.0]

        # Sorting new_row to avoid concatenation warnings
        new_row = dict(sorted(new_row.items()))

        # Concatenating new information about feature importances
        if self.importances_map is not None:
            self.importances_map = pd.concat(
                [self.importances_map, pd.DataFrame(index=[target_series.name], data=new_row)])
        return M

    def reset_importance_map(self, columns):
        # Creating an empty importance map
        if self.importances_map is None:
            self.importances_map = pd.DataFrame(
                data={},
                columns=columns
            )
