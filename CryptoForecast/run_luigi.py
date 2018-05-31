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
from btc.IngestPrices import IngestPrices # ->
from btc.preprocess.DecompressPrices import DecompressPrices  # ->
from btc.preprocess.GroupByTimeStamp import GroupByTimeStamp  # ->
from btc.preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated # ->
from btc.preprocess.BTCMakeStationary import BTCMakeStationary

from btc.preprocess.PlotRawData import PlotRawData  # <- GroupByTimeStamp

from btc.analyze.PlotInflows import PlotInflows
from btc.analyze.BTCSeasonal import BTCSeasonal
from btc.analyze.BTCFFT import BTCFFT

from btc.analyze.BTC_CCF_gtrends import BTC_CCF_gtrends
from btc.model.BTCARIMAX import BTCARIMAX

# === eth
from eth.IngestPrices import IngestPricesETH
from eth.preprocess.PlotRawData import PlotRawDataETH

# === google trends
from googleTrends.IngestGoogleTrends import IngestGoogleTrends  # ->
from googleTrends.preprocess.TrendsInterpolation import TrendsInterpolation
from googleTrends.preprocess.GTrendsMakeStationary import GTrendsMakeStationary

from googleTrends.analyze.TrendsSeasonal import TrendsSeasonal

# === kaggle dataset
from kaggle.analyze.KaggleSeasonal import KaggleSeasonal
from kaggle.analyze.KaggleFFT import KaggleFFT

if __name__ == '__main__':
    luigi.run()
