import pandas as pd


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
