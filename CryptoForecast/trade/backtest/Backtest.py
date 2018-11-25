"""
creates plot of raw data
"""

import luigi
import pandas as pd

import config
from trade.strategy.BollingerBands import BollingerBands
from trade.backtest.fn.bollinger_crossing import bollinger_crossing
from Wallet import Wallet

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

        wallet = Wallet()
        assets = [{
            **wallet.asset_dict(),
            'date_time': dta['Date(UTC)'][0],
            'netHoldings': 0,
            'trade': 0,
        }]

        # Iterate over all rows, adding trade data
        trade_fn = bollinger_crossing
        skip_first_n = 1  # allows calculations to catch up. must be > 1
        # trades = pd.DataFrame(columns=['date_time', 'price', 'trade'])
        for index, row in dta.iterrows():
            if index < skip_first_n:
                continue
            # implied else
            trade_amt = trade_fn(
                price=row['Value'],
                bollinger_lower=row['Lower Band'],
                bollinger_upper=row['Upper Band']
            )
            # if (trade_amt != 0):
            #     trades = trades.append({
            #         "price": row['Value'],
            #         "trade": trade_amt
            #     }, ignore_index=True)
            # else:
            #     trades = trades.append([
            #         row['Date(UTC)'],
            #         row['Value'],
            #         0
            #     ])
        # trades.to_csv(self.output()["trades"].path, index=False)

            if trade_amt != 0:
                wallet.trade(
                    {'btc': - trade_amt},
                    {'eth': - trade_amt / row['Value']},
                )
            assets.append({
                "date_time": row['Date(UTC)'],
                **wallet.asset_dict(),
                "trade": trade_amt
            })

            # Convert values to exchange currency
            assets[-1]['eth'] = assets[-1]['eth'] * row['Value']

            # Calculate net value of holdings
            assets[-1]['netHoldings'] = (
                assets[-1]['btc'] +
                assets[-1]['eth']
            )

        # Convert List to DataFrame
        assets = pd.DataFrame(assets)

        # Write to CSV
        assets.to_csv(self.output().path, index=False)
