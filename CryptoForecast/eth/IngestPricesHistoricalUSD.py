"""
Reads in historical Ethereum price data.
Data from etherscan.io.
"""

import config
import luigi
import requests


class IngestPricesHistoricalETHUSD(luigi.Task):
    def requires(self):
        return []

    def output(self):
        return luigi.LocalTarget(config.data_dir+"ingest/eth_usd_historical.csv")

    def run(self):
        src = "https://etherscan.io/chart/etherprice?output=csv"

        r = requests.get(src, stream=True)

        with open(self.output().path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
