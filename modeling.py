class Modeling:
    def __init__(self):
        self.status = None
        self.model = None
        self.performance_measures = {
            'rmse': {
                'min': -5,
                'max': 5,
                'color': 'blue'
            },
            'corr': {
                'min': 0.3,
                'max': 1,
                'color': 'red'
            }
        }

    def train_model(self, df, var_interest):
        """ Train model
        Receives data and trains the model, updates self.model

        Parameters
        ----------
        df : pandas.DataFrame
            Data to train the model with
        var_interest : str
            Variable to be estimated/predicted
        """
        return

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
        return

    def evaluate_model(self, df):
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
        return