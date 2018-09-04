"""
Outputs Bollinger trade data to plot
"""

import luigi
import pandas
import matplotlib.pyplot as plt
import datetime

import config
from trade.strategy.BollingerBands import BollingerBands

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

        dta.plot(x='Date(UTC)', y='Value')

        dta[['Value', 'EMA', 'STD', 'Upper Band', 'Lower Band']].plot(figsize=config.fig_size)
        plt.title('Bollinger Band for ETH/BTC')
        plt.ylabel('ETH/BTC Exchange Rate')

        plt.savefig(self.output().path, bbox_inches='tight')
