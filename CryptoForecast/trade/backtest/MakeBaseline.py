"""
Runs a bunch of backtests using random dumb trade functions
to establish a baseline against which to compare your "clever" ones.
"""

import luigi
import pandas as pd
import pandas

import config
from trade.backtest.Backtest import TradeFunction
from trade.backtest.Backtest import Backtest
from plotters.ts_compare import ts_compare


class MakeBaseline(luigi.Task):
    n_rands = luigi.IntParameter(
        default=10
    )

    def requires(self):
        return [
            Backtest(
                trade_fn=TradeFunction.random,
                rand_seed=i
            ) for i in range(self.n_rands)
        ]

    def output(self):
        basename = config.data_dir + "trading/backtest_baseline"
        return {
            "csv": luigi.LocalTarget(
                basename + ".csv"
            ),
            "png": luigi.LocalTarget(
                basename + ".png"
            )
        }

    def run(self):
        results = pd.DataFrame()

        for i, backtest in enumerate(self.input()):
            dta = pandas.read_csv(
                backtest.path,
                parse_dates=['date_time'],
            )
            # use dates from 1st backtest
            if i == 0:
                results['date_time'] = dta['date_time']

            # append each net holdings column to the df
            results['r'+str(i)] = dta['netHoldings']

        results.to_csv(self.output()['csv'].path, index=False)
        ts_compare(
            results,
            x_key='date_time',
            savefig=self.output()['png'].path,
            legend=False,
        )
