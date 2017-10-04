"""
unzips raw d/l data
"""

import luigi
import gzip

import config
from btc.IngestPrices import IngestPrices

class DecompressPrices(luigi.Task):

    def requires(self):
        return [IngestPrices()]

    def output(self):
        return luigi.LocalTarget(config.data_dir+"preprocess/coinbaseUSD.csv")

    def run(self):
        with self.input()[0].open('rb') as fin, self.output().open('w') as fout:
            fout.write(fin.read())
