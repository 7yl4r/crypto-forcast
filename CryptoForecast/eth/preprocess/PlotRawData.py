"""
creates plot of raw data.
"""

import luigi
import matplotlib.pyplot as plt
import pandas

import config
from eth.IngestPricesHistorical import IngestPricesHistoricalETH


class PlotRawDataETH(luigi.Task):
    def requires(self):
        return [IngestPricesHistoricalETH()]

    def output(self):
        return luigi.LocalTarget(config.data_dir+"preprocess/eth_rawdata.png")

    def run(self):
        print("\nsaving plot to ", self.output().path, "...\n")
        dta = pandas.read_csv(
            self.input()[0].path,
            names=['Date(UTC)', 'UnixTimeStamp', 'Value'],
            usecols=['Date(UTC)', 'Value'],
            parse_dates=['Date(UTC)'],
            converters={'Value': float},
            skiprows=1  # skip header row
        )

        dta.plot(x='Date(UTC)', y='Value')

        plt.savefig(self.output().path, bbox_inches='tight')
