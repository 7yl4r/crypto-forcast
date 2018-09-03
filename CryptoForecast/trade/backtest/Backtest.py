"""
creates plot of raw data
"""

import luigi
import pandas as pd

import config
from trade.strategy.BollingerBands import BollingerBands


class Backtest(luigi.Task):
    def requires(self):
        return [BollingerBands()]

    def output(self):
        return luigi.LocalTarget(config.data_dir + "trading/backtest_data.csv")

    def run(self):
        # Read input
        print(self.input()[0].path)
        dta = pd.read_csv(
            self.input()[0].path,
            usecols=['Date(UTC)', 'Value', 'Trade'],
            parse_dates=['Date(UTC)'],
            converters={'Value': float},
        )

        assets = [{
            'btcHoldings': config.assets['btc'],
            'ethHoldings': config.assets['eth'],
            'netHoldings': 0
        }]

        for index, row in dta.iterrows():
            lastRow = assets[-1]
            assets.append({
                'btcHoldings': lastRow['btcHoldings'],
                'ethHoldings': lastRow['ethHoldings']
            })

            if (row['Trade'] > 0):
                # buy
                if (row['Value'] * row['Trade'] <= assets[-1]['btcHoldings']):
                    assets[-1]['ethHoldings'] += row['Trade']
                    assets[-1]['btcHoldings'] -= row['Value']

            elif (row['Trade'] < 0):
                # sell
                if (abs(row['Trade']) <= assets[-1]['ethHoldings']):
                    assets[-1]['ethHoldings'] -= abs(row['Trade'])
                    assets[-1]['btcHoldings'] += row['Value']

            # Calculate net value of holdings
            assets[-1]['netHoldings'] = (
                assets[-1]['btcHoldings'] +
                assets[-1]['ethHoldings'] * dta['Value'][index]
            )

        # Convert List to DataFrame
        assets = pd.DataFrame(assets)

        # Merge main DataFrame and assets
        dta = dta.join(assets)

        # Write to CSV
        dta.to_csv(self.output().path, index=False)
