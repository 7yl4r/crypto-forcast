"""
Reads in historical ETH/BTC data.
Data from poloniex.com.
"""

import luigi
import requests
import config

import pandas as pd

class IngestPricesHistoricalETHBTC(luigi.Task):
    def requires(self):
        return []

    def output(self):
        return luigi.LocalTarget(config.data_dir+"ingest/eth_btc_historical.csv")

    def run(self):
        src = "https://poloniex.com/public?command=returnChartData&currencyPair=BTC_ETH&start=1435699200&end=9999999999&period=" + str(config.fidelity)

        r = requests.get(src, stream=True)
        dta = pd.DataFrame(r.json())

        dta['Date(UTC)'] = pd.to_datetime(dta['date'], unit='s')

        dta = dta[['Date(UTC)', 'close']]
        dta = dta.rename(columns={'close': 'Value'})

        dta.to_csv(self.output().path, index=False)
