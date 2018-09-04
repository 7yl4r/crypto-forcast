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
        print(self.input()[0]["trades"].path)
        dta = pd.read_csv(
            self.input()[0]["trades"].path,
            usecols=['date_time', 'price', 'trade'],
            parse_dates=['date_time'],
            converters={'price': float},
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

            if (row['trade'] > 0):
                # buy
                if (row['price'] * row['trade'] <= assets[-1]['btcHoldings']):
                    assets[-1]['ethHoldings'] += row['trade']
                    assets[-1]['btcHoldings'] -= row['price']

            elif (row['trade'] < 0):
                # sell
                if (abs(row['trade']) <= assets[-1]['ethHoldings']):
                    assets[-1]['ethHoldings'] -= abs(row['trade'])
                    assets[-1]['btcHoldings'] += row['price']

            # Calculate net value of holdings
            assets[-1]['netHoldings'] = (
                assets[-1]['btcHoldings'] +
                assets[-1]['ethHoldings'] * dta['price'][index]
            )

        # Convert List to DataFrame
        assets = pd.DataFrame(assets)

        # Merge main DataFrame and assets
        dta = dta.join(assets)

        # Write to CSV
        dta.to_csv(self.output().path, index=False)
