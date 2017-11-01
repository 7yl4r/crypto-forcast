import config
from common.model.ARIMAX import ARIMAX
from googleTrends.preprocess.TrendsInterpolation import TrendsInterpolation
from btc.preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated

class BTCARIMAX(ARIMAX):
    upstream_tasks = [
        TrendsInterpolation,
        Resample2DailyInterpolated
    ]
    outfile_name = config.data_dir+"model/BTCARIMAX.csv"
