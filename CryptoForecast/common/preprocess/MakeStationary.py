"""
uses differencing to make input (more) stationary
"""
import datetime
import logging

import luigi
import pandas
import matplotlib.pyplot as pyplot

import config

class MakeStationary(luigi.Task):
    """Extend this and set the following attributes use it with your data.

    Data is expected to be time-series in csv format with evenly spaced samples.

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
    # NONE

    def requires(self):
        return [self.upstream_task()]

    def output(self):
        return luigi.LocalTarget(self.outfile_name)

    def run(self):
        in_data = pandas.read_csv(
            self.input()[0].path, usecols=[0,1], index_col=0,
            parse_dates=True,
            names=self.col_names, header=0
        )

        diffs = in_data.diff()

        # pyplot.plot(diffs)
        # pyplot.show()

        diffs.to_csv(self.output().path)
