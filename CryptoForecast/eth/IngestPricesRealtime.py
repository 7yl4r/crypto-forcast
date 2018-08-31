"""
Reads in realtime Ethereum price data.
Data from binance.com.
"""

import luigi
from binance.client import Client
import config
import secrets
import pandas as pd
import os.path

client = Client(secrets.binance_key, secrets.binance_secret)

tradingPair = 'ETHBTC'

class IngestPricesRealtimeETH(luigi.Task):
    def requires(self):
        return []

    def complete(self):
        # so that Luigi always re-runs this
        # task, even if output file exists
        return False

    def output(self):
        out = luigi.LocalTarget(config.data_dir + "ingest/ethereum_realtime.csv")
        out.makedirs()
        return out

    def run(self):
        # if saved history exists
        if (os.path.isfile(self.output().path)):
            # import old data
            lastTrades = pd.read_csv(self.output().path)
            lastTrades['time'] = pd.to_datetime(lastTrades['time'])

        # get new trades
        trades = pd.DataFrame(client.get_historical_trades(symbol=tradingPair))

        # convert columns
        trades['time'] = pd.to_datetime(trades['time'], unit='ms', origin='unix')
        trades['price'] = pd.to_numeric(trades['price'])

        # remove irrelevant columns
        trades = trades[['id', 'time','price']]

        if ('lastTrades' in vars()):
            combinedTrades = pd.concat([lastTrades, trades]).drop_duplicates(subset='id')
            combinedTrades.to_csv(self.output().path, index=False)
        else:
            trades.to_csv(self.output().path, index=False)
