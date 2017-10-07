from common.analysis.SeasonalAnalysis import SeasonalAnalysis

from btc.preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated

class BTCSeasonal(SeasonalAnalysis):
    def requires(self):
        return [
            Resample2DailyInterpolated()
        ]

    def output(self):
        return luigi.LocalTarget(config.data_dir+"/analyze/seasonal_month.png")

    col_names=['date','price']
