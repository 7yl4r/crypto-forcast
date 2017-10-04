"""
calculates & plots Cross-Correlation Function with trends data as
exogeneous inflow & price as the outflow
"""

import luigi
import pandas
import matplotlib.pyplot as plt

import config
from preprocess.TrendsInterpolation import TrendsInterpolation
from btc.preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated
from plotters.ccf import plotCCF


class CCF_Trends2Price(luigi.Task):

    def requires(self):
        return [
            TrendsInterpolation(),
            Resample2DailyInterpolated()
        ]

    def output(self):
        return luigi.LocalTarget(config.plot_dir+"CCF_trends2price.png")

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
