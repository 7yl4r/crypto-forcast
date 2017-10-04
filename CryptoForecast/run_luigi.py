#!/usr/bin/env python
"""
loosely inspired by
https://marcobonzanini.com/2015/10/24/building-data-pipelines-with-python-and-luigi/

usage :

`luigid`  # to start the scheduler
`python CryptoForecast/run_luigi.py MyTaskName`  # to queue a task

where MyTaskName is one of the imported task classes below
"""
import luigi

import config

# ====================================================================
# === Task Classes ===================================================
# ====================================================================
# === btc
from btc.IngestPrices import IngestPrices  # ->
from btc.preprocess.DecompressPrices import DecompressPrices  # ->
from btc.preprocess.GroupByTimeStamp import GroupByTimeStamp  # ->
from btc.preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated

from btc.PlotRawData import PlotRawData  # <- GroupByTimeStamp

# === google trends
from googleTrends.IngestGoogleTrends import IngestGoogleTrends  # ->
from googleTrends.preprocess.TrendsInterpolation import TrendsInterpolation

# TODO: port these remaining classes to new org structure:
from vizualize.PlotTrendsAndPrice import PlotTrendsAndPrice
from vizualize.CCF_Trends2Price import CCF_Trends2Price
from vizualize.SeasonalAnalysis import SeasonalAnalysis
from model.ARIMAX_Trends2Price import ARIMAX_Trends2Price

if __name__ == '__main__':
    luigi.run()
