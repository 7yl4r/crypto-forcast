"""
creates plot of raw data
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

class PlotRawData(luigi.Task):

    def requires(self):
        return [GroupByTimeStamp()]

    def output(self):
        return luigi.LocalTarget(config.plot_dir+"data.png")

    def run(self):
        print("\nsaving plot to ", self.output().path, "...\n")
        dta = pandas.read_csv(
            self.input()[0].path, usecols=[0,1], index_col=0,
            parse_dates=True, date_parser=dateparse,
            names=['DateTime', 'price']
        )
        dta.plot(figsize=config.fig_size)

        plt.savefig(self.output().path, bbox_inches='tight')
