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

# Task Classes:
from IngestPrices import IngestPrices
from DecompressPrices import DecompressPrices
from GroupByTimeStamp import GroupByTimeStamp
from PlotRawData import PlotRawData  # this plots grouped price data
from Resample import Resample
from CCF_Trends2Price import CCF_Trends2Price

from IngestGoogleTrends import IngestGoogleTrends
from PlotTrendsAndPrice import PlotTrendsAndPrice

if __name__ == '__main__':
    luigi.run()
