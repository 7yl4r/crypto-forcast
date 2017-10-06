"""
resamples price data to set frequency & cleverly interpolates NaN prices
"""

import datetime

import config
from common.preprocess.Interpolate import Interpolate
from btc.preprocess.GroupByTimeStamp import GroupByTimeStamp

def dateparse (time_in_secs):
    return datetime.datetime.fromtimestamp(float(time_in_secs))

class Resample2DailyInterpolated(Interpolate):
    frequency_str = "D"  # f = 1 / 1 day
    upstream_task = GroupByTimeStamp
    outfile_name = config.data_dir+"preprocess/coinbaseUSD_sampled.csv"
    date_parser = dateparse
    col_names = ['DateTime', 'price']

    @property
    def date_parser(self):
        return dateparse
