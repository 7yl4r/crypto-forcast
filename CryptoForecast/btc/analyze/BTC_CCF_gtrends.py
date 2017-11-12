"""
calculates & plots Cross-Correlation Function with trends data as
exogeneous inflow & price as the outflow
"""

import luigi
import pandas
import matplotlib.pyplot as plt

import config
from googleTrends.preprocess.TrendsInterpolation import TrendsInterpolation
from btc.preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated
from plotters.ccf import plotCCF


class BTC_CCF_gtrends(luigi.Task):

    def requires(self):
        return [
            TrendsInterpolation(),
            Resample2DailyInterpolated()
        ]

    def output(self):
        return luigi.LocalTarget(config.data_dir+"BTC_CCF_gtrends.png")

    def run(self):
        trends_dta = pandas.read_csv(self.input()[0].path, names=['date','trends'], header=0)
        price_dta  = pandas.read_csv(self.input()[1].path, names=['date','price'], header=0)

        merged_inner = pandas.merge(
            left=trends_dta, left_on='date',
            right=price_dta, right_on='date'
        )

        plotCCF(
            merged_inner['price'].astype('float64') ,
            merged_inner['trends'].astype('float64'),
            self.output().path
        )
