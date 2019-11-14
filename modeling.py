from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
import numpy as np
import pandas as pd
from scipy.stats import pearsonr


class Modeling:
    def __init__(self, settings):
        self.status = None
        self.model = None
        self.predictions = None
        self.last_prediction_dt = None
        self.monitor = None
        self.monitor_measures = {
            'rmse': {
                'min': -1,
                'max': 1,
                'color': 'blue'
            },
            'corr_y2y4': {
                'min': 1,
                'max': -1,
                'color': 'red'
            },
            'corr_y2y3': {
                'min': -1,
                'max': 1,
                'color': 'green'
            },
            'corr_u1y3': {
                'min': -1,
                'max': 1,
                'color': 'brown'
            },
            'corr_u2y2': {
                'min': -1,
                'max': 1,
                'color': 'orange'
            }
        }
        self.settings = settings

    def reset(self):
        self.status = None
        self.model = None
        self.predictions = None
        self.last_prediction_dt = None
        self.monitor = None

    def train_model(self, df, params):
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
        # self.model = MLPRegressor(hidden_layer_sizes=(10,), activation='tanh')
        self.model.fit(X_train, y_train)

        y_train_pred = self.model.predict(X_train)

        rmse_train = np.sqrt(((y_train_pred - y_train) ** 2).mean())

        messages = 'Linear regression model trained. Training RMSE = {0}. Params: {1}.'.format(rmse_train, str(params))

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
            if len(df):
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

    def monitor_model(self, df, df_preds):
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

        df_performance = pd.DataFrame(columns=list(self.monitor_measures.keys()))
        if len(df) < 60:
            return None
        else:
            df_performance.loc[0, time_var] = self.last_prediction_dt

        df_preds = df_preds.iloc[-60:]
        df = df.iloc[-60:]
        df_performance.loc[0, 'rmse'] = np.sqrt(((df_preds[output_prediction] - df[output]) ** 2).mean())
        df_performance.loc[0, 'corr_y2y4'] = pearsonr(df['y2'], df['y4'])[0]
        df_performance.loc[0, 'corr_y2y3'] = pearsonr(df['y2'], df['y3'])[0]
        df_performance.loc[0, 'corr_u1y3'] = pearsonr(df['u1'], df['y3'])[0]
        df_performance.loc[0, 'corr_u2y2'] = pearsonr(df['u2'], df['y2'])[0]
        # df_performance.loc[0, 'y3'] = df['y3'].mean()

        try:
            self.monitor = self.monitor.append(df_performance, ignore_index=True).reset_index(drop=True)
        except Exception as e:
            self.monitor = df_performance

        return self.monitor
