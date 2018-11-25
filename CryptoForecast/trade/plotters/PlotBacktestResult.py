"""
Outputs Bollinger trade data to plot
"""

import luigi
import pandas
import matplotlib.pyplot as plt
import altair as alt

import config
from trade.backtest.Backtest import Backtest


class PlotBacktestResult(luigi.Task):
    def requires(self):
        return [Backtest()]

    def output(self):
        return luigi.LocalTarget(config.data_dir+"trading/backtest.png")

    def run(self):
        print("\nsaving plot to ", self.output().path, "...\n")
        dta = pandas.read_csv(
            self.input()[0].path,
            parse_dates=['date_time'],
        )

        # from vega_datasets import data
        # source = data.unemployment_across_industries.url
        dta = pandas.melt(
            dta,
            id_vars=['date_time'],
            value_vars=['btc', 'eth'],
            var_name='coin',
            value_name='amount',
        )
        print(dta.info())

        alt.Chart(dta).mark_area().encode(
            alt.X(
                'date_time:T',
                axis=alt.Axis(format='%Y', domain=False, tickSize=0)
            ),
            alt.Y('amount:Q', stack='center', axis=None),
            alt.Color(
                'coin:N',
                scale=alt.Scale(scheme='category20b')
            )
        ).save(config.data_dir+"trading/backtest.png")
        # dta.plot(x='date_time', y='Value')
        #
        # dta[['Value', 'EMA', 'STD', 'Upper Band', 'Lower Band']].plot(
        #     figsize=config.fig_size
        # )
        # plt.title('Bollinger Band for ETH/BTC')
        # plt.ylabel('ETH/BTC Exchange Rate')
        #
        # plt.savefig(self.output().path, bbox_inches='tight')
