from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
import pickle

class Modeling:
    def __init__(self, settings):
        self.status = None
        self.model = None
        self.predictions = None
        self.last_prediction_dt = '0'
        self.monitor = None
        self.monitor_measures = {
            'rmse': {
                'min': -1,
                'max': 1,
                'color': 'blue'
            },
            'y2': {
                'min': 0.2,
                'max': 1,
                'color': 'red'
            },
            'y4-y2': {
                'min': 0.4,
                'max': -0.4,
                'color': 'green'
            }
        }
        self.settings = settings

    def reset(self):
        self.status = None
        self.model = None
        self.predictions = None
        self.last_prediction_dt = None
        self.monitor = None

    def transform(self, df_raw, features, feat_lags):
        max_lag = 0
        for feat in feat_lags:
            lags = feat_lags[feat]

            for lag in lags:
                df_raw[feat + 'l' + str(lag)] = df_raw[feat].shift(lag)

            if lag > max_lag:
                max_lag = lag

        df = df_raw.iloc[max_lag:]
        df = df[['dt'] + features]

        return df

    def train_model(self, df, params):
        """ Train model
        Receives data and trains the model, updates self.model

        Parameters
        ----------
        df : pandas.DataFrame
            Data to train the model with
        """
        feat_lags = self.settings['feat_lags']
        features = self.settings['features']
        df_features = self.transform(df, features, feat_lags)

        X_train = df_features[self.settings['features']].values
        y_train = df.loc[df_features.index, self.settings['output']].values

        self.model = LinearRegression()
        # self.model = MLPRegressor(hidden_layer_sizes=(10,), activation='tanh')
        self.model.fit(X_train, y_train)

        y_train_pred = self.model.predict(X_train)

        rmse_train = np.sqrt(((y_train_pred - y_train) ** 2).mean())

        messages = 'Linear regression model trained. Training RMSE = {0}. Params: {1}.'.format(rmse_train, str(params))

        self.status = 'trained'

        return messages

    def load(self, path_model):
        self.model = pickle.load(open(path_model, 'rb'))
        self.status = 'trained'

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
            try:
                df = df.loc[df[time_var] > self.last_prediction_dt]
            except:
                df_preds = df[[time_var]]
                df_preds[output_prediction] = 0
                self.predictions = df_preds
                self.last_prediction_dt = self.predictions[time_var].max()

            if len(df) > 1:
                predict_with_model = True

        if predict_with_model:
            """
            The follows two lines are the ones that should be changed to run the model
            """
            feat_lags = self.settings['feat_lags']
            features = self.settings['features']
            df_features = self.transform(df,  features, feat_lags)

            X_pred = df_features[features].values
            y_pred = self.model.predict(X_pred)

            df_preds = pd.DataFrame(columns=[time_var, output_prediction])
            dt_pred = df_features[time_var].values
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
        df = df.loc[df_preds.index]
        df_performance.loc[0, 'y4-y2'] = (df['y4'] - df['y2']).mean()

        df_preds = df_preds.iloc[-60:]
        df = df.loc[df_preds.index]
        df_performance.loc[0, 'rmse'] = np.sqrt(((df_preds[output_prediction] - df[output]) ** 2).mean())
        df_performance.loc[0, 'y2'] = df['y2'].mean()

        try:
            self.monitor = self.monitor.append(df_performance, ignore_index=True).reset_index(drop=True)
        except Exception as e:
            self.monitor = df_performance

        return self.monitor
