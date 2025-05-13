from typing import Optional

import numpy as np
import optuna
import pandas as pd
from loguru import logger
from sklearn.impute import SimpleImputer
from sklearn.linear_model import HuberRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


class BaselineModel:
    def __init__(self):
        """
        Provide initial parameters to initialize the model.
        """
        pass

    def fit(self, X, y):
        """
        Fit the model to the data.
        """
        pass

    def predict(self, X) -> pd.Series:
        """
        Predict the target variable.
        """
        return X['close']


def generate_lazypredict_model_table(
    X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series
) -> pd.DataFrame:
    """
    Uses lazypredict to fit N models with default hyperparameters for the given
    (X_train, y_train), and evaluate them with (X_test, y_test)


    """
    # unset the MLFLOW_TRACKING_URI
    import os

    mlflow_tracking_uri = os.environ['MLFLOW_TRACKING_URI']
    del os.environ['MLFLOW_TRACKING_URI']

    from lazypredict.Supervised import LazyRegressor
    from sklearn.metrics import mean_absolute_error

    reg = LazyRegressor(
        verbose=0, ignore_warnings=False, custom_metric=mean_absolute_error
    )
    models, _ = reg.fit(X_train, X_test, y_train, y_test)

    # reset the index so that the model names are in the first column
    models.reset_index(inplace=True)

    # set the MLFLOW_TRACKING_URI back to its original value
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri

    return models


# class that fits and  a huber regression model
class HuberRegressionModel_hyperparameter_tuning:
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        number_of_trials: Optional[int] = 0,
        number_of_folds: Optional[int] = 0,
    ):
        """
        Fit the model to the data.
        args:
            X: pd.DataFrame training data,
            y: pd.Series target variable,
            number_of_trials: int,
            number_of_folds: int,
        """
        self.number_of_trials = number_of_trials
        self.number_of_folds = number_of_folds
        logger.info(
            f'Fitting the model to the data with {number_of_trials} trials and {number_of_folds} folds'
        )

        best_hyperparameters = self._tune_hyperparameters(X, y)

        # import simple imputer and standard scaler
        from sklearn.impute import SimpleImputer
        from sklearn.preprocessing import StandardScaler

        pipeline = Pipeline(
            [
                ('imputer', SimpleImputer(strategy='mean')),
                ('scaler', StandardScaler()),
                ('model', HuberRegressor(**best_hyperparameters)),
            ]
        )
        self.pipeline = pipeline.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.pipeline.predict(X)

    def _tune_hyperparameters(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
    ) -> dict:
        """
        finds the best hyperparameters for the model using bayesian optimization
        args:
            X_train: pd.DataFrame training data,
            y_train: pd.Series target variable,
        returns:
            best_hyperparameters: dict
        """

        # creating objective function
        def objective(trial: optuna.Trial) -> float:
            # creating params dictionary
            params = {
                'epsilon': trial.suggest_float('epsilon', 1, 999999),
                'max_iter': trial.suggest_int('max_iter', 100, 1000),
                'tol': trial.suggest_float('tol', 1e-5, 1),
                'alpha': trial.suggest_float('alpha', 0.0001, 1.0),
                'fit_intercept': trial.suggest_categorical(
                    'fit_intercept', [True, False]
                ),
                'warm_start': trial.suggest_categorical('warm_start', [True, False]),
            }

            # splitting time series data into train and test sets using time series split
            from sklearn.model_selection import TimeSeriesSplit

            tscv = TimeSeriesSplit(n_splits=self.number_of_folds)
            mae_scores = []

            # splitting the data into train and validation sets folds
            for train_index, val_index in tscv.split(X_train):
                X_train_fold, X_val_fold = (
                    X_train.iloc[train_index],
                    X_train.iloc[val_index],
                )
                y_train_fold, y_val_fold = (
                    y_train.iloc[train_index],
                    y_train.iloc[val_index],
                )

            # preprocessing the data

            # use standard scaler to scale the data and drop null values
            # drop null values
            pipeline = Pipeline(
                [
                    ('imputer', SimpleImputer(strategy='mean')),
                    ('scaler', StandardScaler()),
                    ('model', HuberRegressor(**params)),
                ]
            )

            # training the model on training fold
            pipeline.fit(X_train_fold, y_train_fold)

            # evaluating the model on validation fold
            y_pred = pipeline.predict(X_val_fold)
            mae_scores.append(mean_absolute_error(y_val_fold, y_pred))

            # returning the mean of the mae scores
            return np.mean(mae_scores)

        # creating optuna study
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=self.number_of_trials)

        return study.best_trial.params
