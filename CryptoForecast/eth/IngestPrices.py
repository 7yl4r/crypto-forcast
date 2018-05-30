"""
Reads in Ethereum price data from ingest source.
Data from etherscan.io.
"""

import luigi
import requests
import config

class IngestPricesETH(luigi.Task):
    def requires(self):
        return []

    def output(self):
        return luigi.LocalTarget(config.data_dir+"ingest/ethereum.csv")

    def run(self):
        src = "https://etherscan.io/chart/etherprice?output=csv"

        r = requests.get(src, stream=True)

        with self.output().open('w') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
