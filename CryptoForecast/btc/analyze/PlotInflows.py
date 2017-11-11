import luigi

import config
from googleTrends.preprocess.TrendsInterpolation import TrendsInterpolation
from btc.preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated
from common.analyze.PlotMultipleScaledTimeSeries import PlotMultipleScaledTimeSeries

class PlotInflows(PlotMultipleScaledTimeSeries):
    def requires(self):
        return [
            TrendsInterpolation(),
            Resample2DailyInterpolated()
        ]

    def output(self):
        return luigi.LocalTarget(config.data_dir+"/preprocess/btc-inflows.png")
