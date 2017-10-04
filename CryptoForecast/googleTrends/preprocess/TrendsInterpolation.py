"""
interpolates missing trends values
"""

import luigi
import numpy as np
import pandas
import matplotlib.pyplot as plt
import datetime

import config
from googleTrends.IngestGoogleTrends import IngestGoogleTrends

class TrendsInterpolation(luigi.Task):
    frequency_str = "D"  # f = 1 / 1 day

    def requires(self):
        return [IngestGoogleTrends()]

    def output(self):
        return luigi.LocalTarget(config.data_dir+"preprocess/bitcoin_trends_interpolated.csv")

    def run(self):
        print("\ndownsampling to f=1/(" + self.frequency_str + ")...\n")
        dta = pandas.read_csv(
            self.input()[0].path, usecols=[0,1], index_col=0,
            parse_dates=True,
            names=['DateTime', 'bitcoin'], header=0
        )
        daily_df = dta.resample(self.frequency_str).mean()
        daily_df = daily_df.interpolate(method='linear')
        daily_df.to_csv(self.output().path)
