#!/usr/bin/env python
"""
loosely inspired by
https://marcobonzanini.com/2015/10/24/building-data-pipelines-with-python-and-luigi/
"""
import luigi

import config
from IngestPrices import IngestPrices
from DecompressPrices import DecompressPrices
from GroupByTimeStamp import GroupByTimeStamp
from PlotRawData import PlotRawData
from Resample import Resample

if __name__ == '__main__':
    luigi.run()
