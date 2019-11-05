import os
import pandas as pd
import datetime as dt


class Simulator:
    def __init__(self, path_stream_data, path_database):
        self.path = path_database
        self.path_stream = path_stream_data

    def start(self):
        self.stream = pd.read_csv(self.path_stream, parse_dates=['dt'])
        self.stream = self.stream.sort_values('dt')
        self.time_start = self.stream['dt'].min()
        self.time = self.stream['dt'].min()

        self.stream.iloc[:0].to_csv(self.path, index=None)
        self.step(seconds=0)

    def step(self, seconds=5):
        self.time = self.time + dt.timedelta(seconds=seconds)

        df_stream = self.stream
        out_data = df_stream.loc[df_stream['dt'] <= self.time]

        if len(out_data):
            with open(self.path, 'a') as f:
                out_data.to_csv(f, header=False, index=None)

            df_stream = df_stream.loc[df_stream['dt'] > self.time]

            self.stream = df_stream

    def read_db(self):
        df = pd.read_csv(self.path)
        return df


if __name__ == '__main__':
    # Testing Simulator
    path_project = os.path.abspath(
        os.path.join(os.path.realpath(__file__), '..')
    )

    path_stream_data = os.path.join(path_project, 'database', 'raw_data.csv')
    path_database = os.path.join(path_project, 'database', 'database.csv')

    sim = Simulator(path_stream_data, path_database)
    sim.start()

    for i in range(50):
        sim.step(seconds=1)
        print('RAW DATA:')
        print(sim.stream)
        print('DATABASE:')
        print(pd.read_csv(path_database))