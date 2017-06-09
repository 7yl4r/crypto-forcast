"""
creates plot of raw data
"""

import luigi
import numpy as np
import pandas
import matplotlib.pyplot as plt
import datetime

import config
from IngestGoogleTrends import IngestGoogleTrends
from Resample import Resample

def dateparse (time_in_secs):
    return datetime.datetime.fromtimestamp(float(time_in_secs))

class PlotTrendsAndPrice(luigi.Task):

    def requires(self):
        return [
            IngestGoogleTrends(),
            Resample()
        ]

    def output(self):
        return luigi.LocalTarget(config.plot_dir+"trends.png")

    def run(self):
        trends_dta = pandas.read_csv(self.input()[0].path)
        price_dta = pandas.read_csv(self.input()[1].path)
        ax = trends_dta.plot(figsize=config.fig_size)
        price_dta.plot(ax=ax, figsize=config.fig_size)

        print("\nsaving plot to ", self.output().path, "...\n")
        plt.savefig(self.output().path, bbox_inches='tight')

        # TODO: also plot price on here from Resample or GroupByTimeStamp
