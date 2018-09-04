"""
Strategy for trading with Bollinger Band indicators.

Parameters:
- ewmInterval: interval to be used for calculating moving averages
- tradeAmount: amount, in ETH, to trade every time

"""

import luigi
import pandas as pd

import config
from eth.IngestPricesHistoricalBTC import IngestPricesHistoricalETHBTC


class BollingerBands(luigi.Task):
    def requires(self):
        return [IngestPricesHistoricalETHBTC()]

    def output(self):
        outs = {
            "trades": luigi.LocalTarget(
                config.data_dir + "trading/trades_bollinger.csv"
            ),
            "bollinger": luigi.LocalTarget(
                config.data_dir + "analyze/bollinger.csv"
            )
        }
        for out in outs:
            outs[out].makedirs()
        return outs

    def run(self):
        if (config.ewmInterval < config.fidelity):
            raise ValueError(
                'config.ewmInterval must be >= to config.fidelity'
            )

        # Read input
        dta = pd.read_csv(
            self.input()[0].path,
            parse_dates=['Date(UTC)'],
            converters={'Value': float}
        )

        ###################
        # Calculate bands #
        ###################

        # Get interval. Example: ewmInterval is 86400 * 20 (20 days),
        # fidelity is 86400 (1 day). Resulting interval is 20.
        interval = config.ewmInterval / config.fidelity

        dta['EMA'] = dta['Value'].ewm(span=interval).mean()
        dta['STD'] = dta['Value'].ewm(span=interval).std()
        dta['Upper Band'] = dta['EMA'] + (dta['STD'] * config.stdK)
        dta['Lower Band'] = dta['EMA'] - (dta['STD'] * config.stdK)

        # Iterate over all rows, adding trade data
        trades = pd.DataFrame(columns=['date_time', 'price', 'trade'])
        for index, row in dta.iterrows():
            if (row['Value'] <= row['Lower Band']):
                trades = trades.append({
                    "date_time": row['Date(UTC)'],
                    "price": row['Value'],
                    "trade": config.tradeAmount
                }, ignore_index=True)
            elif (row['Value'] >= row['Upper Band']):
                trades = trades.append({
                    "date_time": row['Date(UTC)'],
                    "price": row['Value'],
                    "trade": -config.tradeAmount
                }, ignore_index=True)
            # else:
            #     trades = trades.append([
            #         row['Date(UTC)'],
            #         row['Value'],
            #         0
            #     ])
        # dta['Trade'] = trades

        # Export
        dta.to_csv(self.output()["bollinger"].path, index=False)
        trades.to_csv(self.output()["trades"].path, index=False)
