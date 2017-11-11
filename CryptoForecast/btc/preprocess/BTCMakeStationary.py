"""
resamples price data to set frequency & cleverly interpolates NaN prices
"""

import datetime

import config
from common.preprocess.MakeStationary import MakeStationary
from btc.preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated

class BTCMakeStationary(MakeStationary):
    upstream_task = Resample2DailyInterpolated
    outfile_name = config.data_dir+"preprocess/BTC_stationary.csv"
    col_names = ['DateTime', 'price']
