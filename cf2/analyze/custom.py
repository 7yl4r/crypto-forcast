import matplotlib.pyplot as plt
import numpy as np

from catalyst.exchange.utils.stats_utils import extract_transactions
# from catalyst.api import get_environment

from plo7y.ts_compare.horizongraph import Horizon

DPI = None  # 100
PLT_SIZE = (9, 5)


def add_plt(perf_data, rows, cols, n, varname):
    ax1 = plt.subplot(rows, cols, n)
    perf_data.loc[:, [varname]].plot(ax=ax1)
    ax1.legend_.remove()
    ax1.set_ylabel('{}'.format(varname))
    start, end = ax1.get_ylim()
    ax1.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))
    plt.tight_layout()


def plot_all_perfs(perf_data):
    """
    NOTE: has been replaced by horizongraph.

    Exploratory plot of a lot of perf data.
    """
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
    NOTE: has been replaced by horizongraph.

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


def horizon(perf_data, varnames, outfile_name):
    plt.clf()
    # data = perf_data.loc[:, [vname]]
    # print(dir(data))
    # print(data)
    da_y = [
        list(perf_data.loc[:, [vname]][vname].values)
        for vname in varnames
    ]
    print('---da_y--------------------------')
    print('max={} | min={} | len=[{}x{}]'.format(
        max(max(da_y)), min(min(da_y)), len(da_y), len(da_y[0])
    ))
    print('---da_x--------------------------')
    # assume all have same x
    # da_x = perf_data.loc[:, ['portfolio_value']].index.values
    da_x = range(len(perf_data.loc[:, ['portfolio_value']].index.values))
    print(da_x)
    print('---labels =?= da_y----------------')
    labels = varnames  # ['portfolio_value']
    print('{} =?= {}'.format(len(da_y), len(labels)))

    plot = Horizon().run(da_x, da_y, labels, bands=3, figsize=PLT_SIZE)

    plot.subplots_adjust(left=0.01, right=0.998, top=0.99, bottom=0.01)
    plt.savefig(outfile_name, dpi=DPI)
    plt.clf()


def tutorial_plt2(context, results):
    plt.clf()
    # Plot the portfolio and asset data.
    ax1 = plt.subplot(611)
    results[['portfolio_value']].plot(ax=ax1)
    ax1.set_ylabel('Portfolio Value (USD)')

    ax2 = plt.subplot(612, sharex=ax1)
    ax2.set_ylabel('{asset} (USD)'.format(asset=context.ASSET_NAME))
    (context.TICK_SIZE * results[['price']]).plot(ax=ax2)

    # NOTE: !!! this throws an error, so we're skipping it for now
    # trans = results.ix[[t != [] for t in results.transactions]]
    # buys = trans.ix[
    #     [t[0]['amount'] > 0 for t in trans.transactions]
    # ]
    # ax2.plot(
    #     buys.index,
    #     context.TICK_SIZE * results.price[buys.index],
    #     '^',
    #     markersize=10,
    #     color='g',
    # )

    ax3 = plt.subplot(613, sharex=ax1)
    results[['leverage', 'alpha', 'beta']].plot(ax=ax3)
    ax3.set_ylabel('Leverage ')

    ax4 = plt.subplot(614, sharex=ax1)
    results[['starting_cash', 'cash']].plot(ax=ax4)
    ax4.set_ylabel('Cash (USD)')

    results[[
        'treasury',
        'algorithm',
        'benchmark',
    ]] = results[[
        'treasury_period_return',
        'algorithm_period_return',
        'benchmark_period_return',
    ]]

    ax5 = plt.subplot(615, sharex=ax1)
    results[[
        'treasury',
        'algorithm',
        'benchmark',
    ]].plot(ax=ax5)
    ax5.set_ylabel('Percent Change')

    ax6 = plt.subplot(616, sharex=ax1)
    results[['volume']].plot(ax=ax6)
    ax6.set_ylabel('Volume (mCoins/5min)')

    plt.legend(loc=3)

    # Show the plot.
    plt.gcf().set_size_inches(18, 8)
    plt.savefig("figures/tut2.png", bbox_inches='tight')
    plt.clf()


def analyze(context, perf):
    horizon(
        perf,
        varnames=[
            'portfolio_value',
            # 'price_change',  # KeyError

            'ending_cash',
            "gross_leverage",

            'net_leverage',
            'ending_value',
            'short_exposure',

            'long_exposure',

            'longs_count',
            'shorts_count',

            'volume',  # too big magnitude; throws off scale of others
        ],
        outfile_name="figures/horizon.png",
    )
    horizon(
        perf,
        varnames=[
            'rsi_16',
            'rsi_8',
            'rsi_4',
            'rsi_2',
            'rsi_02',
            # 'weight_2',
            # 'weight_4',
            # 'weight_8',
            # 'weight_16',
            'rsi_pressure',
            'centering_force',
            'net_force',
            'amount_to_buy',
        ],
        outfile_name="figures/forces.png",
    )
    horizon(
        perf,
        varnames=[
            'positions_asset',
            'cash',
            'percent_asset',
        ],
        outfile_name="figures/portfolio_composition.png",
    )
    tutorial_plt1(context, perf)
    tutorial_plt2(context, perf)
    # TODO: something useful with this?:
    # perf_tracker = perf.PerformanceTracker(
    #     sim_params, get_calendar("NYSE"), env
    # )
    distribution_check(
        perf,
        [
            'rsi_02',
            'rsi_2',
            'rsi_4',
            'rsi_8',
            'rsi_16',
            'rsi_pressure',
            'centering_force',
            'net_force',
        ]
    )


def distribution_check(perf_data, vnames):
    plt.clf()
    cols = 1
    rows = len(vnames)+1
    for n, vname in enumerate(vnames):
        ax_n = plt.subplot(rows, cols, n+1)
        data_frame = perf_data.loc[:, vname]
        data_frame.plot.hist(
            ax=ax_n,
            # label=vname,
            # range=(0, 100),
        )
        plt.ylabel(vname)
        plt.xlim(-1, 1)
    plt.savefig("figures/distributions.png", bbox_inches='tight')


def tutorial_plt1(context, perf):
    # Get the quote_currency that was passed as a parameter to the simulation
    exchange = list(context.exchanges.values())[0]
    quote_currency = exchange.quote_currency.upper()
    rows = 1
    cols = 1

    # Second chart: Plot asset price, moving averages and buys/sells
    ax2 = plt.subplot(rows, cols, 1)
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

    # First chart: Plot portfolio value using quote_currency
    # ax2 = plt.subplot(rows, cols, 1, sharex=ax1)
    # perf.loc[:, ['portfolio_value']].plot(ax=ax1)
    # ax1.legend_.remove()
    # ax1.set_ylabel('Portfolio Value\n({})'.format(quote_currency))
    # start, end = ax1.get_ylim()
    # ax1.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    # # Third chart: Compare percentage change between our portfolio
    # # and the price of the asset
    # ax3 = plt.subplot(rows, cols, 3, sharex=ax1)
    # perf.loc[:, ['algorithm_period_return', 'price_change']].plot(ax=ax3)
    # ax3.legend_.remove()
    # ax3.set_ylabel('Percent Change')
    # start, end = ax3.get_ylim()
    # ax3.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    # # Fourth chart: Plot our cash
    # ax4 = plt.subplot(rows, cols, 4, sharex=ax1)
    # perf.ending_cash.plot(ax=ax4)
    # ax4.set_ylabel('ending_cash\n({})'.format(quote_currency))
    # start, end = ax4.get_ylim()
    # ax4.yaxis.set_ticks(np.arange(0, end, end / 5))

    # plt.show()
    plt.gcf().set_size_inches(PLT_SIZE)
    plt.savefig("figures/tut1.png", bbox_inches='tight')
