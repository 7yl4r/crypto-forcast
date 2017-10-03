"""
performs seasonal decomposition to analyze data
"""

import luigi
import pandas
import matplotlib.pyplot as plt

import config
from preprocess.TrendsInterpolation import TrendsInterpolation
from preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated
from plotters.seasonalDecompose import seasonalDecompose


class SeasonalAnalysis(luigi.Task):

    def requires(self):
        return [
            TrendsInterpolation(),
            Resample2DailyInterpolated()
        ]

    def output(self):
        return luigi.LocalTarget(config.plot_dir+"seasonal_month.png")

    def run(self):
        trends_dta = pandas.read_csv(self.input()[0].path, names=['date','trends'], header=0)
        price_dta  = pandas.read_csv(self.input()[1].path, names=['date','price'], header=0)

        merged_inner = pandas.merge(
            left=trends_dta, left_on='date',
            right=price_dta, right_on='date'
        )

        seasonalDecompose(
            merged_inner['price'].astype('float64'),
            saveFigName=self.output().path,
            dataResolution=1,
            seasonLen=30
        )

        #     merged_inner['trends'].astype('float64'),
