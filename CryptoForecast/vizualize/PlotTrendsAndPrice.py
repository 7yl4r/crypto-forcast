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
from preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated

def dateparse (time_in_secs):
    return datetime.datetime.fromtimestamp(float(time_in_secs))

class PlotTrendsAndPrice(luigi.Task):

    def requires(self):
        return [
            IngestGoogleTrends(),
            Resample2DailyInterpolated()
        ]

    def output(self):
        return luigi.LocalTarget(config.plot_dir+"trends.png")

    def run(self):
        trends_dta = pandas.read_csv(self.input()[0].path, index_col=0)
        price_dta = pandas.read_csv(self.input()[1].path, index_col=0)

        plt.plot(
            [datetime.datetime.strptime(d, '%Y-%m-%d') for d in trends_dta.index],
            [price_dta.price.max()/100.0 * v for v in trends_dta.bitcoin]  # scale trends percentage
        )
        plt.plot(
            [datetime.datetime.strptime(d, '%Y-%m-%d') for d in price_dta.index],
            price_dta.price
        )
        # ax = trends_dta.plot(figsize=config.fig_size, x='Date', y='bitcoin', sharex=True)
        # price_dta.plot(ax=ax, figsize=config.fig_size, x='Date', y='price', sharex=True)

        print("\nsaving plot to ", self.output().path, "...\n")
        plt.savefig(self.output().path, bbox_inches='tight')
