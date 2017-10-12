import luigi

import config
from common.analyze.SeasonalAnalysis import SeasonalAnalysis
from btc.preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated

class BTCSeasonal(SeasonalAnalysis):
    def requires(self):
        return [
            Resample2DailyInterpolated()
        ]

    def output(self):
        return [
            luigi.LocalTarget(config.data_dir+"/analyze/btc_seasonal.results")
        ]

    col_names=['date','price']
