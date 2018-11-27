"""
Runs a bunch of backtests using random dumb trade functions
to establish a baseline against which to compare your "clever" ones.
"""

import luigi
import pandas as pd
import pandas

import config
from trade.backtest.MakeBaseline import MakeBaseline
from trade.backtest.Backtest import Backtest
from plotters.ts_compare import ts_compare


class AnalyzeBacktestResult(luigi.Task):
    def requires(self):
        return {
            "backtest": Backtest(),
            "baseline": MakeBaseline()
        }

    def output(self):
        basename = config.data_dir + "trading/backtest_eval"
        return {
            "csv": luigi.LocalTarget(
                basename + ".csv"
            ),
            "png": luigi.LocalTarget(
                basename + ".png"
            )
        }

    def run(self):
        backtest_dta = pandas.read_csv(
            self.input()["backtest"].path,
            parse_dates=['date_time'],
        )
        baseline_dta = pandas.read_csv(
            self.input()["baseline"]["csv"].path,
            parse_dates=['date_time'],
        )
        results = []
        # assume same # rows
        assert len(backtest_dta) == len(baseline_dta)
        for i, row in backtest_dta.iterrows():
            # print(row)
            val = row['netHoldings']
            n_bested = 0
            n_worsted = 0
            for baseline in baseline_dta:
                # for each baseline_column
                # all cols except date_time are baselines
                if baseline == "date_time":
                    continue
                elif baseline_dta[baseline][i] < val:
                    n_bested += 1
                else:
                    # tie goes to the baseline
                    assert baseline_dta[baseline][i] >= val
                    n_worsted += 1
            assert n_worsted + n_bested == len(baseline_dta.columns) - 1
            percentile = n_bested / (n_bested + n_worsted)
            results.append([row['date_time'], percentile])

        results = pd.DataFrame(
            results,
            columns=["date_time", "percentile"]
        )
        results.to_csv(self.output()['csv'].path, index=False)
        ts_compare(
            results,
            x_key='date_time',
            savefig=self.output()['png'].path,
            legend=False,
        )
