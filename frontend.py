import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from simulator import Simulator
import pandas as pd
import plotly.graph_objects as go

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

app.layout = html.Div(children=[
    # Storage in application for database
    dcc.Store(id='store-database'),
    dcc.Store(id='store-clock'),
    # Div for controls
    html.Div([
        html.Button('Start simulation', id='button-start-simulation',
                    n_clicks_timestamp=0, style={'backgroundColor': colors['light-green']}),
        html.Button('Pause simulation', id='button-pause-simulation',
                    n_clicks_timestamp=0, style={'margin-left': '10px', 'backgroundColor': colors['light-yellow']}),
        html.Button('Reset simulation', id='button-reset-simulation',
                    n_clicks_timestamp=0, style={'margin-left': '10px', 'backgroundColor': colors['light-red']}),
    ],
        style={'backgroundColor': colors['yellow'],
               'padding': '10px'}
    ),
    # Div for row 2 (spaces 1 and 2)
    html.Div([
        # Div for space 1
        html.Div([
            html.H3('Column 1'),
            dcc.Graph(id='graph-sensors')
        ], className="six columns"),
        # Div for space 2
        html.Div([
            html.H3('Column 2'),
            dcc.Graph(id='g2', figure={'data': [{'y': [1, 2, 3]}]})
        ], className="six columns"),
    ], className="row"),
    # Div for row 3 (spaces 3 and 4)
    html.Div([
        # Div for space 3
        html.Div([
            html.H3('Column 3'),
            dcc.Graph(id='g3', figure={'data': [{'y': [1, 2, 3]}]})
        ], className="six columns"),
        # Div for space 4
        html.Div([
            html.H3('Column 4'),
            dcc.Graph(id='g4', figure={'data': [{'y': [1, 2, 3]}]})
        ], className="six columns"),
    ], className="row"),
    dcc.Interval(
            id='interval-component',
            interval=60*60*1000, # in milliseconds
            n_intervals=0
    )
])


@app.callback(Output('graph-sensors', 'figure'),
              [Input('store-database', 'data')])
def update_graphs(database):
    if database is not None:
        df_database = pd.DataFrame.from_records(database)
        df_sensors = pd.pivot_table(df_database, index=['dt'], columns=['sensor'], values='value').reset_index()

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df_sensors['dt'], y=df_sensors['s1'],
                                 mode='lines+markers',
                                 name='s1'))

        fig.add_trace(go.Scatter(x=df_sensors['dt'], y=df_sensors['s2'],
                                 mode='lines+markers',
                                 name='s2'))

        fig.add_trace(go.Scatter(x=df_sensors['dt'], y=df_sensors['g2'],
                                 mode='lines+markers',
                                 name='g2'))

        return fig

    else:
        return {}


@app.callback(Output('interval-component', 'interval'),
              [Input('button-start-simulation', 'n_clicks_timestamp'),
               Input('button-pause-simulation', 'n_clicks_timestamp'),
               Input('button-reset-simulation', 'n_clicks_timestamp')])
def start_simulation(n_start, n_pause, n_reset):
    if int(n_start) > int(n_pause) and int(n_start) > int(n_reset):
        return 1 * 1000
    elif int(n_pause) > int(n_start) and int(n_pause) > int(n_reset):
        return 60 * 60 * 1000
    elif int(n_reset) > int(n_start) and int(n_reset) > int(n_pause):
        sim.start()
        return 1 * 1000
    else:
        return 60 * 60 * 1000

@app.callback([Output('store-database', 'data'),
               Output('store-clock', 'data')],
              [Input('interval-component', 'n_intervals')],
              [State('store-clock', 'data')])
def update_database(n, clock):
    if n != 0:
        sim.step(1)
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

if __name__ == '__main__':
    app.run_server(debug=True)

