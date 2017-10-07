import luigi

import config
from common.analyze.SeasonalAnalysis import SeasonalAnalysis
from googleTrends.preprocess.TrendsInterpolation import TrendsInterpolation

class TrendsSeasonal(SeasonalAnalysis):
    def requires(self):
        return [
            TrendsInterpolation()
        ]

    def output(self):
        return luigi.LocalTarget(config.data_dir+"/analyze/trends_seasonal.results")

    col_names=['date','bitcoin']
