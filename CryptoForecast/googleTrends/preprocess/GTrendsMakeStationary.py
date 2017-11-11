"""
resamples price data to set frequency & cleverly interpolates NaN prices
"""

import datetime

import config
from common.preprocess.MakeStationary import MakeStationary
from googleTrends.preprocess.TrendsInterpolation import TrendsInterpolation

class GTrendsMakeStationary(MakeStationary):
    upstream_task = TrendsInterpolation
    outfile_name = config.data_dir+"preprocess/gTrends_stationary.csv"
    col_names = ['DateTime', 'value']
