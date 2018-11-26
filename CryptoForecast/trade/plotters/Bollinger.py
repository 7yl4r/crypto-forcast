"""
Outputs Bollinger trade data to plot
"""

import luigi
import pandas

import config
from trade.strategy.BollingerBands import BollingerBands
from plotters.ts_compare import ts_compare


class PlotBollinger(luigi.Task):
    def requires(self):
        return [BollingerBands()]

    def output(self):
        return luigi.LocalTarget(config.data_dir+"trading/bollinger.png")

    def run(self):
        print("\nsaving plot to ", self.output().path, "...\n")
        dta = pandas.read_csv(
            self.input()[0]["bollinger"].path,
            parse_dates=['Date(UTC)'],
            converters={'Value': float},
        )
        print(dta.info())
        ts_compare(
            dta,
            x_key='Date(UTC)',
            y_key_list=['Value', 'EMA', 'STD', 'Upper Band', 'Lower Band'],
            figsize=config.fig_size,
            title='Bollinger Band for ETH/BTC',
            ylabel='ETH/BTC Exchange Rate',
            savefig=self.output().path
        )
