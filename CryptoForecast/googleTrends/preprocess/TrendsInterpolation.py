"""
interpolates missing trends values
"""

import config
from common.preprocess.Interpolate import Interpolate
from googleTrends.IngestGoogleTrends import IngestGoogleTrends

class TrendsInterpolation(Interpolate):
    frequency_str = "D"
    upstream_task = IngestGoogleTrends
    outfile_name = config.data_dir+"preprocess/bitcoin_trends_interpolated.csv"
    col_names = ['DateTime', 'bitcoin']
    header = 0
