import luigi

import config
from googleTrends.preprocess.TrendsInterpolation import TrendsInterpolation
from btc.preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated
from common.model.PlotMultipleScaledTimeSeries import PlotMultipleScaledTimeSeries

class PlotInflows(PlotScaledTimeSeries):
    def requires(self):
        return [
            TrendsInterpolation(),
            Resample2DailyInterpolated()
        ]

    def output(self):
        return luigi.LocalTarget(config.data_dir+"/preprocess/btc-inflows.png")
