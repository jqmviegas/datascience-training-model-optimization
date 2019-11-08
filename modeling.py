from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import pandas as pd


class Modeling:
    def __init__(self, settings):
        self.status = None
        self.model = None
        self.predictions = None
        self.last_prediction_dt = None
        self.performance = None
        self.performance_measures = {
            'rmse': {
                'min': -1,
                'max': 1,
                'color': 'blue'
            },
            'corr': {
                'min': 0.6,
                'max': -0.6,
                'color': 'red'
            }
        }
        self.settings = settings

    def reset(self):
        self.status = None
        self.model = None
        self.predictions = None
        self.last_prediction_dt = None
        self.performance = None

    def train_model(self, df):
        """ Train model
        Receives data and trains the model, updates self.model

        Parameters
        ----------
        df : pandas.DataFrame
            Data to train the model with
        """
        X_train = df[self.settings['inputs']].values
        y_train = df[self.settings['output']].values

        self.model = LinearRegression()
        self.model.fit(X_train, y_train)

        y_train_pred = self.model.predict(X_train)

        rmse_train = np.sqrt(((y_train_pred - y_train) ** 2).mean())

        messages = 'Linear regression model trained. Training RMSE = {0}'.format(rmse_train)

        self.status = 'trained'

        return messages

    def run_model(self, df):
        """ Run model
        Receives data and estimated the variable of interest

        Parameters
        ----------
        df : pandas.DataFrame
            Data to run the model on

        Returns
        -------
        df : pandas.DataFrame
            Output data
        """
        time_var = self.settings['time_var']
        output_prediction = self.settings['output']+'_prediction'
        predict_with_model = False

        if self.status is None:
            df_preds = df[[time_var]]
            df_preds[output_prediction] = 0
            self.predictions = df_preds
            self.last_prediction_dt = self.predictions[time_var].max()
        else:
            df = df.loc[df[time_var] > self.last_prediction_dt]
            predict_with_model = True

        if predict_with_model:
            """
            The follows two lines are the ones that should be changed to run the model
            """
            X_pred = df[self.settings['inputs']].values
            y_pred = self.model.predict(X_pred)

            df_preds = pd.DataFrame(columns=[time_var, output_prediction])
            dt_pred = df[time_var].values
            df_preds[time_var] = dt_pred
            df_preds[output_prediction] = y_pred
            self.predictions = self.predictions.append(df_preds, ignore_index=True).reset_index(drop=True)
            self.last_prediction_dt = self.predictions[time_var].max()

        return self.predictions

    def evaluate_model(self, df, df_preds):
        """ Evaluate model performance

        Parameters
        ----------
        df : pandas.DataFrame
            Data to evaluate the model on

        Returns
        -------
        df_performance : pandas.DataFrame
            Data with performance measures for the model over time
        """
        time_var = self.settings['time_var']
        output = self.settings['output']
        output_prediction = self.settings['output']+'_prediction'

        df_performance = pd.DataFrame(columns=list(self.performance_measures.keys()))
        if self.status is None:
            return None
        else:
            df_performance.loc[0, time_var] = self.last_prediction_dt

        df_preds = df_preds.iloc[-10:]
        df = df.iloc[-10:]
        df_performance.loc[0, 'rmse'] = np.sqrt(((df_preds[output_prediction] - df[output]) ** 2).mean())
        df_performance.loc[0, 'corr'] = r2_score(df[output], df_preds[output_prediction])

        try:
            self.performance = self.performance.append(df_performance, ignore_index=True).reset_index(drop=True)
        except Exception as e:
            self.performance = df_performance

        return self.performance
