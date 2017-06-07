"""
reads in data from ingest sources (in configuration files?)
"""

import luigi
import urllib

import config

class IngestPrices(luigi.Task):

    def requires(self):
        return []

    def output(self):
        return luigi.LocalTarget(config.data_dir+"coinbaseUSD.csv.gz")

    def run(self):
        # with self.output().open('w') as f:
        src = "http://api.bitcoincharts.com/v1/csv/coinbaseUSD.csv.gz"
        testfile = urllib.URLopener()
        testfile.retrieve(src, self.output())
