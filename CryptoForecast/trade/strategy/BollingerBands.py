"""
Strategy for trading with Bollinger Band indicators.
"""

import luigi
import pandas as pd
import matplotlib.pyplot as plt
import datetime

import config
from eth.IngestPricesHistorical import IngestPricesHistoricalETH

class BollingerBands(luigi.Task):
    def requires(self):
        return [IngestPricesHistoricalETH()]

    def output(self):
        return luigi.LocalTarget(config.data_dir + "trading/trades.csv")

    def run(self):
        # Read input
        dta = pd.read_csv(
          self.input()[0].path,
          names=['Date(UTC)', 'UnixTimeStamp', 'Value'],
          usecols=['Date(UTC)','Value'],
          parse_dates=['Date(UTC)'],
          converters={'Value': float},
          skiprows=1 # skip header row
        )

        # Calculate bands
        dta['30 Day EMA'] = dta['Value'].ewm(span=30).mean()
        dta['30 Day STD'] = dta['Value'].ewm(span=30).std()
        dta['Upper Band'] = dta['30 Day EMA'] + (dta['30 Day STD'] * 2)
        dta['Lower Band'] = dta['30 Day EMA'] - (dta['30 Day STD'] * 2)

        # Iterate over all rows, adding trade data
        trades = []
        for index, row in dta.iterrows():
            if (row['Value'] <= row['Lower Band']):
                trades.append(1)
            elif (row['Value'] >= row['Upper Band']):
                trades.append(-1)
            else:
                trades.append(0)

        dta['Trade'] = trades

        # Export
        dta.to_csv(self.output().path)
        '''
        print(dta)
        dta[['Value', '30 Day MA', 'Upper Band', 'Lower Band']].plot(figsize=(12,6))
        plt.title('30 Day Bollinger Band for Facebook')
        plt.ylabel('Price (USD)')
        plt.show();
        '''
