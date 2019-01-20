import matplotlib.pyplot as plt
import numpy as np

from catalyst.exchange.utils.stats_utils import extract_transactions
# from catalyst.api import get_environment

from plo7y.ts_compare.horizongraph import Horizon

DPI = 110


def add_plt(perf_data, rows, cols, n, varname):
    ax1 = plt.subplot(rows, cols, n)
    perf_data.loc[:, [varname]].plot(ax=ax1)
    ax1.legend_.remove()
    ax1.set_ylabel('{}'.format(varname))
    start, end = ax1.get_ylim()
    ax1.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))
    plt.tight_layout()


def plot_all_perfs(perf_data):
    plt.clf()
    rows = 3
    cols = 2
    add_plt(perf_data, rows, cols, 1, "gross_leverage")
    add_plt(perf_data, rows, cols, 2, 'net_leverage')
    add_plt(perf_data, rows, cols, 3, 'long_exposure')
    add_plt(perf_data, rows, cols, 4, 'longs_count')
    add_plt(perf_data, rows, cols, 5, 'short_exposure')
    add_plt(perf_data, rows, cols, 6, 'shorts_count')
    plt.savefig("figures/all_perfs.png", dpi=DPI)
    plt.clf()


def values(perf_data):
    plt.clf()
    rows = 2
    cols = 1
    add_plt(perf_data, rows, cols, 1, 'net_value')
    plt.savefig("figures/values.png", dpi=DPI)
    plt.clf()


def val_cash_portfolio_check(perf_data):
    """
    Verifies that
     'portfolio_value': self.ending_cash + self.ending_value,
    """
    plt.clf()
    rows = 2
    cols = 2
    add_plt(perf_data, rows, cols, 1, 'ending_cash')
    add_plt(perf_data, rows, cols, 2, 'ending_value')
    add_plt(perf_data, rows, cols, 3, 'portfolio_value')
    plt.savefig("figures/cash_n_val_check.png", dpi=DPI)
    plt.clf()


def horizon(perf_data):
    plt.clf()
    varnames = [
        'ending_cash', 'ending_value', 'portfolio_value'
    ]
    # TODO:
    # da_y = [perf_data.loc[:, [varn]] for varn in varnames]
    # da_x = range(len(da_y[0]))  # assume all have same x?
    da_y = perf_data.loc[:, ['portfolio_value']]
    da_x = range(len(da_y))  # assume all have same x?
    plot = Horizon().run(da_x, da_y, varnames, bands=3)
    plot.subplots_adjust(left=0.07, right=0.998, top=0.99, bottom=0.01)
    plt.savefig("figures/horizon.png", dpi=DPI)
    plt.clf()


def analyze(context, perf):
    # Get the quote_currency that was passed as a parameter to the simulation
    exchange = list(context.exchanges.values())[0]
    quote_currency = exchange.quote_currency.upper()

    plot_all_perfs(perf)
    val_cash_portfolio_check(perf)
    horizon(perf)

    rows = 4
    cols = 1
    # First chart: Plot portfolio value using quote_currency
    ax1 = plt.subplot(rows, cols, 1)
    perf.loc[:, ['portfolio_value']].plot(ax=ax1)
    ax1.legend_.remove()
    ax1.set_ylabel('Portfolio Value\n({})'.format(quote_currency))
    start, end = ax1.get_ylim()
    ax1.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    # Second chart: Plot asset price, moving averages and buys/sells
    ax2 = plt.subplot(rows, cols, 2, sharex=ax1)
    perf.loc[:, ['price', 'short_mavg', 'long_mavg']].plot(
        ax=ax2,
        label='Price'
    )
    ax2.legend_.remove()
    ax2.set_ylabel('{asset}\n({quote})'.format(
        asset=context.asset.symbol,
        quote=quote_currency
    ))
    start, end = ax2.get_ylim()
    ax2.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    transaction_df = extract_transactions(perf)
    if not transaction_df.empty:
        buy_df = transaction_df[transaction_df['amount'] > 0]
        sell_df = transaction_df[transaction_df['amount'] < 0]
        ax2.scatter(
            buy_df.index.to_pydatetime(),
            perf.loc[buy_df.index, 'price'],
            marker='^',
            s=100,
            c='green',
            label=''
        )
        ax2.scatter(
            sell_df.index.to_pydatetime(),
            perf.loc[sell_df.index, 'price'],
            marker='v',
            s=100,
            c='red',
            label=''
        )

    # Third chart: Compare percentage change between our portfolio
    # and the price of the asset
    ax3 = plt.subplot(rows, cols, 3, sharex=ax1)
    perf.loc[:, ['algorithm_period_return', 'price_change']].plot(ax=ax3)
    ax3.legend_.remove()
    ax3.set_ylabel('Percent Change')
    start, end = ax3.get_ylim()
    ax3.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    # Fourth chart: Plot our cash
    ax4 = plt.subplot(rows, cols, 4, sharex=ax1)
    perf.ending_cash.plot(ax=ax4)
    ax4.set_ylabel('ending_cash\n({})'.format(quote_currency))
    start, end = ax4.get_ylim()
    ax4.yaxis.set_ticks(np.arange(0, end, end / 5))

    # plt.show()
    plt.savefig("figures/analyze_dual_ma.png", bbox_inches='tight')

    # TODO: RSI plot(s)?
    # freq = get_environment('data_frequency')
    # if freq == 'daily':
    #     rsi_freq = '1D'
    # elif freq == 'minute':
    #     rsi_freq = '1m'
    # else:
    #     raise ValueError('unknown data_freq "{}"'.format(freq))
    # prices = data.history(
    #     context.asset,
    #     fields='price',
    #     bar_count=20,
    #     frequency=rsi_freq
    # )
    # # Relative Strength Index (RSI)
    # rsi = talib.RSI(prices.values, timeperiod=context.TIMEPERIOD)[-1]

    # TODO: something useful with this?:
    # perf_tracker = perf.PerformanceTracker(
    #     sim_params, get_calendar("NYSE"), env
    # )
