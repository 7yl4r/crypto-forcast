#!/usr/bin/env python
"""
collection of luigi tasks aimed at backtesting trading functions

usage:
------
`luigid`  # start the scheduler
`python CryptoForecast/luigi_backtests.py MyTaskName`  # queue a task

where MyTaskName is one of the imported task classes below

examples:
---------
python CryptoForecast/luigi_backtests.py PlotBacktestResult --BollingerBands-stdK 0.7

python CryptoForecast/luigi_backtests.py PlotBacktestResult --BollingerBands-stdK 0.7 --Backtest-trade-fn b_cross_bal
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
