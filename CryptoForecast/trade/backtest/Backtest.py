"""
creates plot of raw data
"""

import luigi
import pandas as pd

import config
from trade.strategy.BollingerBands import BollingerBands
from trade.backtest.fn.bollinger_crossing import bollinger_crossing


class Backtest(luigi.Task):
    def requires(self):
        return [BollingerBands()]

    def output(self):
        return luigi.LocalTarget(config.data_dir + "trading/backtest_data.csv")

    def run(self):
        # Read input
        print(self.input()[0]["bollinger"].path)
        dta = pd.read_csv(
            self.input()[0]["bollinger"].path,
            usecols=[
                'Date(UTC)', 'Value', 'EMA', 'STD', 'Upper Band', 'Lower Band'
            ],
            parse_dates=['Date(UTC)'],
            converters={
                'Value': float,
                'EMA': float,
                'STD': float,
                'Upper Band': float,
                'Lower Band': float,
            },
        )

        assets = [{
            'date_time': dta['Date(UTC)'][0],
            'btcHoldings': config.assets['btc'],
            'ethHoldings': config.assets['eth'],
            'netHoldings': 0
        }]

        # Iterate over all rows, adding trade data
        trade_fn = bollinger_crossing
        skip_first_n = 1  # allows calculations to catch up. must be > 1
        trades = pd.DataFrame(columns=['date_time', 'price', 'trade'])
        for index, row in dta.iterrows():
            lastRow = assets[-1]
            if index < skip_first_n:
                continue
            # implied else
            trade_amt = trade_fn(
                price=row['Value'],
                bollinger_lower=row['Lower Band'],
                bollinger_upper=row['Upper Band']
            )
            if (trade_amt != 0):
                trades = trades.append({
                    "price": row['Value'],
                    "trade": trade_amt
                }, ignore_index=True)
            # else:
            #     trades = trades.append([
            #         row['Date(UTC)'],
            #         row['Value'],
            #         0
            #     ])
        # trades.to_csv(self.output()["trades"].path, index=False)

            assets.append({
                "date_time": row['Date(UTC)'],
                'btcHoldings': lastRow['btcHoldings'],
                'ethHoldings': lastRow['ethHoldings']
            })

            if (trade_amt > 0):
                # buy
                if (row['Value'] * trade_amt <= assets[-1]['btcHoldings']):
                    assets[-1]['ethHoldings'] += trade_amt
                    assets[-1]['btcHoldings'] -= row['Value']

            elif (trade_amt < 0):
                # sell
                if (abs(row['Value']) <= assets[-1]['ethHoldings']):
                    assets[-1]['ethHoldings'] -= abs(trade_amt)
                    assets[-1]['btcHoldings'] += row['Value']

            # Calculate net value of holdings
            assets[-1]['netHoldings'] = (
                assets[-1]['btcHoldings'] +
                assets[-1]['ethHoldings'] * row['Value']
            )

        # Convert List to DataFrame
        assets = pd.DataFrame(assets)

        # Merge main DataFrame and assets
        # dta = dta.join(assets)

        # Write to CSV
        assets.to_csv(self.output().path, index=False)
