"""
"""

import luigi
import pandas as pd
import enum
from math import floor
import random
import sys

import config
from trade.strategy.BollingerBands import BollingerBands
from trade.backtest.fn.bollinger_crossing import bollinger_crossing
from trade.backtest.fn.bollinger_cross_balanced import bollinger_cross_balanced
from trade.backtest.fn.random import random as random_trade
from Wallet import Wallet


class TradeFunction(enum.Enum):
    # strings for use as parameters
    b_cross = 'bollinger_crossing'
    b_cross_bal = 'bollinger_cross_balance'
    random = 'random'

trade_function_map = {
    # then map strings to actual functions
    # (because luigi breaks on funcion enums)
    'bollinger_crossing': bollinger_crossing,
    'bollinger_cross_balance': bollinger_cross_balanced,
    'random': random_trade,
}


class Backtest(luigi.Task):
    trade_fn = luigi.EnumParameter(
        enum=TradeFunction,
        default=TradeFunction.b_cross
    )
    rand_seed = luigi.IntParameter(
        default=random.randrange(sys.maxsize)
    )

    def requires(self):
        return [BollingerBands()]

    def output(self):
        return luigi.LocalTarget(
            config.data_dir + "trading/backtest_{}_{}.csv".format(
                self.trade_fn,
                self.rand_seed
            )
        )

    def run(self):
        random.seed(self.rand_seed)
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
                # 'STD': float,
                # 'Upper Band': float,
                # 'Lower Band': float,
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
        skip_first_n = 1  # allows calculations to catch up. must be > 1
        # trades = pd.DataFrame(columns=['date_time', 'price', 'trade'])
        for index, row in dta.iterrows():
            if index < skip_first_n:
                continue
            # implied else
            trade_amt = trade_function_map[self.trade_fn.value](
                price=row['Value'],
                bollinger_lower=row['Lower Band'],
                bollinger_upper=row['Upper Band'],
                max_trade=floor(assets[-1]['btc']*0.5),
                eth_btc_ratio=(1+assets[-1]['eth']) / (1+assets[-1]['btc']),
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

            trade_penalty = .05
            if trade_amt != 0:
                wallet.trade(
                    {'btc': - trade_amt},
                    {'eth': - trade_amt / row['Value'] * (1 - trade_penalty)},
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
        self.assets_df = assets  # for external access in MakeBaseline
        # Write to CSV
        assets.to_csv(self.output().path, index=False)
