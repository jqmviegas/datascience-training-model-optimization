import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from simulator import Simulator
from modeling import Modeling
import pandas as pd
import plotly.graph_objects as go

settings = {
    'inputs': [
        'u1',
        'u2'
    ],
    'unknown': [
        'y2',
        'y3',
        'y4'
    ],
    'output': 'y1',
    'time_var': 'dt'
}

time_var = settings['time_var']
output = settings['output']
output_model = output+'_prediction'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'grey': '#797878',
    'yellow': '#FFDB00',
    'light-green': '#90ee90',
    'light-yellow': '#ffffed',
    'light-red': '#ffcccb'
}

path_project = os.path.abspath(
    os.path.join(os.path.realpath(__file__), '..')
)

path_stream_data = os.path.join(path_project, 'database', 'raw_data.csv')
path_database = os.path.join(path_project, 'database', 'database.csv')

sim = Simulator(path_stream_data, path_database)
model = Modeling(settings)

app.layout = html.Div(children=[
    # Storage in application for database
    dcc.Store(id='store-database'),
    dcc.Store(id='store-clock'),
    # Div for controls
    html.Div([
        html.Div([
            html.H6('Digital Twin'),
        ], className='four columns', style={'padding-left': '10px'}),
        html.Div([
            html.Button('Start', id='button-start-simulation',
                        n_clicks_timestamp=0,
                        style={'backgroundColor': colors['light-green'], 'borderColor': 'yellow'}),
            html.Button('Pause', id='button-pause-simulation',
                        n_clicks_timestamp=0, style={'margin-left': '10px', 'backgroundColor': colors['light-yellow'],
                                                     'borderColor': 'yellow'}),
            html.Button('Reset', id='button-reset-simulation',
                        n_clicks_timestamp=0, style={'margin-left': '10px', 'backgroundColor': colors['light-red'],
                                                     'borderColor': 'yellow'}),
        ], className='four columns', style={'margin-top': '5px'})
    ],
        className='row',
        style={'backgroundColor': colors['yellow'],
               'padding': '10px'}
    ),
    # Div for row 2 (spaces 1 and 2)
    html.Div([
        # Div for space 1
        html.Div([
            html.H3('Sensors'),
            dcc.Graph(id='graph-sensors')
        ], className="six columns"),
        # Div for space 2
        html.Div([
            html.H3('Output'),
            dcc.Graph(id='graph-interest')
        ], className="six columns"),
    ], className="row"),
    # Div for row 3 (spaces 3 and 4)
    html.Div([
        # Div for space 3
        html.Div([
            html.H3('Model training'),
            html.Div([
                dcc.Input(
                    placeholder='Parameter 1...', id='input-1',
                    type='text', value=''
                ),
                dcc.Input(
                    placeholder='Parameter 2...', id='input-2',
                    type='text', value='', style={'margin-left': '10px'}
                ),
            ], className='row'),
            html.Div([
                html.Button('Train model (base struct)', id='button-train-model', n_clicks_timestamp=0,
                            style={'margin-top': '10px', 'background-color': colors['yellow'],
                                   'margin-right': '10px'}),
                html.Button('Train model (change struct)', id='button-train-model-struct', n_clicks_timestamp=0,
                            style={'margin-top': '10px', 'background-color': colors['yellow'],
                                   'margin-bottom': '10px'}),
            ], className='row'),
            html.H6('Modeling messages:'),
            html.P(id='modeling-messages')
        ], className="six columns"),
        # Div for space 4
        html.Div([
            html.H3('Monitoring'),
            dcc.Graph(id='graph-monitoring')
        ], className="six columns"),
    ], className="row"),
    dcc.Interval(
            id='interval-component',
            interval=60*60*1000, # in milliseconds
            n_intervals=0
    )
])


def pivot_sensors(df):
    """
    Returns the pivoted data of sensors
    """
    df_sensors = pd.pivot_table(df, index=[time_var], columns=['sensor'], values='value').reset_index()
    df_sensors[time_var] = pd.to_datetime(df_sensors[time_var])

    return df_sensors


@app.callback([Output('graph-sensors', 'figure'),
               Output('graph-interest', 'figure'),
               Output('graph-monitoring', 'figure')],
              [Input('store-database', 'data')])
def update_graphs(database):
    if database is not None:
        df_database = pd.DataFrame.from_records(database)
        df_sensors = pivot_sensors(df_database)

        print(len(df_sensors))

        fig_sensors = go.Figure()

        for input in settings['inputs']:
            fig_sensors.add_trace(go.Scatter(x=df_sensors[time_var], y=df_sensors[input],
                                     mode='lines',
                                     name=input))

        for input in settings['unknown']:
            fig_sensors.add_trace(go.Scatter(x=df_sensors[time_var], y=df_sensors[input],
                                     mode='lines',
                                     name=input))

        # Run model here to present output (if it exists)
        fig_interest = go.Figure()

        fig_interest.add_trace(go.Scatter(x=df_sensors[time_var], y=df_sensors[output],
                                         mode='lines',
                                         name=output))

        df_preds = model.run_model(df_sensors)

        fig_interest.add_trace(go.Scatter(x=df_preds[time_var], y=df_preds[output_model],
                                         mode='lines',
                                         name=output_model))


        # Evaluate measures here if, at least show the upper and lower limits
        df_performance = df_sensors.copy()
        performance_measures = model.monitor_measures
        performance_lines = []

        fig_performance = go.Figure()

        for measure in performance_measures:
            min_col = 'Min. {}'.format(measure)
            max_col = 'Max. {}'.format(measure)
            df_performance[min_col] = performance_measures[measure]['min']
            df_performance[max_col] = performance_measures[measure]['max']

            performance_lines.append(min_col)
            performance_lines.append(max_col)

            color = performance_measures[measure]['color']

            fig_performance.add_trace(go.Scatter(x=df_performance[time_var], y=df_performance[min_col],
                                                 mode='lines',
                                                 name=min_col,
                                                 line=dict(dash='dot', color=color)))

            fig_performance.add_trace(go.Scatter(x=df_performance[time_var], y=df_performance[max_col],
                                                 mode='lines',
                                                 name=max_col,
                                                 line=dict(dash='dot', color=color)))

        df_performance_values = model.monitor_model(df_sensors, df_preds)

        if df_performance_values is not None:
            for measure in performance_measures:
                color = performance_measures[measure]['color']

                fig_performance.add_trace(go.Scatter(x=df_performance_values[time_var], y=df_performance_values[measure],
                                                     mode='lines',
                                                     name=measure,
                                                     line=dict(color=color)))

        if len(df_sensors) > 200:
            fig_sensors.layout.xaxis.range = [df_sensors.iloc[-200][time_var], df_sensors.iloc[-1][time_var]]
            fig_interest.layout.xaxis.range = [df_sensors.iloc[-200][time_var], df_sensors.iloc[-1][time_var]]
            fig_performance.layout.xaxis.range = [df_sensors.iloc[-200][time_var], df_sensors.iloc[-1][time_var]]

        return fig_sensors, fig_interest, fig_performance

    else:
        return {}, {}, {}


@app.callback(Output('interval-component', 'interval'),
              [Input('button-start-simulation', 'n_clicks_timestamp'),
               Input('button-pause-simulation', 'n_clicks_timestamp'),
               Input('button-reset-simulation', 'n_clicks_timestamp')])
def start_simulation(n_start, n_pause, n_reset):
    if int(n_start) > int(n_pause) and int(n_start) > int(n_reset):
        return 5 * 1000
    elif int(n_pause) > int(n_start) and int(n_pause) > int(n_reset):
        return 60 * 60 * 1000
    elif int(n_reset) > int(n_start) and int(n_reset) > int(n_pause):
        sim.start()
        model.reset()
        return 5 * 1000
    else:
        return 60 * 60 * 1000


@app.callback([Output('store-database', 'data'),
               Output('store-clock', 'data')],
              [Input('interval-component', 'n_intervals')],
              [State('store-clock', 'data')])
def update_database(n, clock):
    if n != 0:
        sim.step(60*10)
    else:
        sim.start()

    database = sim.read_db()

    if clock is None:
        clock = 0
        print(clock)
    else:
        clock += 1
        print('clock {}'.format(clock))

    return database.to_dict('records'), clock


@app.callback(Output('modeling-messages', 'children'),
              [Input('button-train-model', 'n_clicks_timestamp'),
               Input('button-train-model-struct', 'n_clicks_timestamp')],
              [State('store-database', 'data'),
               State('input-1', 'value'),
               State('input-2', 'value')])
def start_simulation(n_train, n_train_struct, database, param1, param2):
    params = {
        'param1': param1,
        'param2': param2
    }

    if int(n_train) > int(n_train_struct):
        df_database = pd.DataFrame.from_records(database)
        df_sensors = pivot_sensors(df_database)

        train_log = model.train_model(df_sensors, params)

        return train_log
    elif int(n_train_struct) > int(n_train):
        df_database = pd.DataFrame.from_records(database)
        df_sensors = pivot_sensors(df_database)

        train_log = model.train_model(df_sensors, params)

        return train_log
    else:
        train_log = 'No model currently trained.'
        return train_log


if __name__ == '__main__':
    app.run_server(debug=True)
