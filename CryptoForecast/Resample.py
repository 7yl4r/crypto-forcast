"""
creates plot of raw data
"""

import luigi
import numpy as np
import pandas
import matplotlib.pyplot as plt
import datetime

import config
from GroupByTimeStamp import GroupByTimeStamp

def dateparse (time_in_secs):
    return datetime.datetime.fromtimestamp(float(time_in_secs))

class Resample(luigi.Task):
    frequency_str = "D"  # f = 1 / 1 day

    def requires(self):
        return [GroupByTimeStamp()]

    def output(self):
        return luigi.LocalTarget(config.data_dir+"coinbaseUSD_sampled.csv")

    def run(self):
        print("\ndownsampling to f=1/(" + self.frequency_str + ")...\n")
        dta = pandas.read_csv(
            self.input()[0].path, usecols=[0,1], index_col=0,
            parse_dates=True, date_parser=dateparse,
            names=['DateTime', 'price']
        )
        daily_df = dta.resample(self.frequency_str).mean()

        daily_df.to_csv(self.output().path)
