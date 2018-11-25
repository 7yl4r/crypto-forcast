#!/usr/bin/env python
"""
Methods for running backtests

usage :

`luigid`  # start the scheduler
`python CryptoForecast/luigi_backtests.py MyTaskName`  # queue a task

where MyTaskName is one of the imported task classes below
"""
import luigi
import config

# === trading
from trade.backtest.Backtest import Backtest
from trade.plotters.PlotBacktestResult import PlotBacktestResult

# TODO: + trading calculator task to backtest using a TaskParameter :
# https://luigi.readthedocs.io/en/stable/api/luigi.parameter.html#luigi.parameter.TaskParameter

if __name__ == '__main__':
    luigi.run()
