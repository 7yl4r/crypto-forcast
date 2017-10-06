"""
resamples price data to set frequency & cleverly interpolates NaN prices
"""

import luigi
import numpy as np
import pandas
import matplotlib.pyplot as plt
import datetime

import config
from btc.preprocess.GroupByTimeStamp import GroupByTimeStamp

def dateparse (time_in_secs):
    return datetime.datetime.fromtimestamp(float(time_in_secs))

class Interpolate(luigi.Task):
    """Extend this and set the following attributes use it with your data.

    Data is expected to be in csv format.

    Required Attributes
    ----------
    upstream_task : luigi.Task
        Task whose output we use here. Output should be csv data file.
    outfile_name : file path string
        Path to output file.
    col_names : str []
        Column names of upstream file data.
    """

    # Optional Attributes
    # ----------
    @property
    def date_parser():
        return None  # (function)
    #    Function to parse dates from date column.
    header = None  # (?)
    #    passthrough to pandas.read_csv

    frequency_str = luigi.Parameter(
        default="D",  # f = 1 / 1 day
        description="Desired sampling period.",
        # positional=True,
        # always_in_help=False,
        # batch_method=None
    )

    def requires(self):
        return [self.upstream_task()]

    def output(self):
        return luigi.LocalTarget(self.outfile_name)

    def run(self):
        print("\ndownsampling to f=1/(" + self.frequency_str + ")...\n")
        dta = pandas.read_csv(
            self.input()[0].path, usecols=[0,1], index_col=0,
            parse_dates=True,
            names=self.col_names, header=self.header, date_parser=self.date_parser
        )
        daily_df = dta.resample(self.frequency_str).mean()
        daily_df = daily_df.interpolate(method='linear', axis=1).ffill().bfill()  # NOTE: axis=1).ffill().bfill() was not present in TrendsInterpolation previously... is this okay or do we need another parameter?
        daily_df.to_csv(self.output().path)
