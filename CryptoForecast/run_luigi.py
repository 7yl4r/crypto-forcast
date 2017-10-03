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

# === Task Classes:
# ingest
from IngestPrices import IngestPrices
from IngestGoogleTrends import IngestGoogleTrends

# preprocess
from preprocess.DecompressPrices import DecompressPrices
from preprocess.GroupByTimeStamp import GroupByTimeStamp
from preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated

from preprocess.TrendsInterpolation import TrendsInterpolation

# visualization
from vizualize.PlotRawData import PlotRawData  # this plots grouped price data
from vizualize.PlotTrendsAndPrice import PlotTrendsAndPrice
from vizualize.CCF_Trends2Price import CCF_Trends2Price
from vizualize.SeasonalAnalysis import SeasonalAnalysis

# model
from model.ARIMAX_Trends2Price import ARIMAX_Trends2Price

if __name__ == '__main__':
    luigi.run()
