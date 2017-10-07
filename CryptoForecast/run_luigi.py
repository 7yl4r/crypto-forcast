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

from btc.preprocess.PlotRawData import PlotRawData  # <- GroupByTimeStamp

from btc.model.PlotInflows import PlotInflows as BTCInflows
from btc.analyze.BTCSeasonal import BTCSeasonal

# === google trends
from googleTrends.IngestGoogleTrends import IngestGoogleTrends  # ->
from googleTrends.preprocess.TrendsInterpolation import TrendsInterpolation

from googleTrends.analyze.TrendsSeasonal import TrendsSeasonal

# TODO: port these remaining classes to new org structure:
from vizualize.CCF_Trends2Price import CCF_Trends2Price
from model.ARIMAX_Trends2Price import ARIMAX_Trends2Price

if __name__ == '__main__':
    luigi.run()
