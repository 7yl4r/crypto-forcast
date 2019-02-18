from logbook import Logger
from catalyst.api import order
# from catalyst.api import order_target_percent
from catalyst.api import symbol
from catalyst.api import record
from catalyst.api import get_environment
from catalyst.utils.run_algo import run_algorithm
import talib
import pandas as pd
import numpy

from analyze.custom import analyze
from FlexyIndicator import FlexyIndicator

ALGO_NAMESPACE = 'buy_the_dip_live'
log = Logger('buy low sell high')


def initialize(context):
    log.info('initializing algo')
    context.ASSET_NAME = 'eth_btc'
    context.asset = symbol(context.ASSET_NAME)

    # === alrgorithm calculation settings
    # === buy/sell order settings
    # TODO: scale these according to portfolio balance
    context.MIN_TRADE = 0.1
    context.MAX_TRADE = 0.5
    context.SLIPPAGE_ALLOWED = 0.02  # [%]

    context.TARGET_POSITION_PERCENT = 50.0
    # # === TODO: set initial amount to target percent
    # cash = context.portfolio.cash
    # coins_value = cash * context.TARGET_POSITION_PERCENT / 100
    # # price = data.current(context.asset, 'price')
    # # price = context.asset.price
    # price = 28.0  # TODO: get this
    # # n coins * BTC/coin = asset_value (in BTC)
    # n_coins = coins_value / price
    # context.portfolio.positions[context.asset].amount = n_coins
    # context.portfolio.cash -= coins_value
    # # portfolio_value = coins_value + cash

    # NOTE: I don't know what these are and what they do:
    context.PROFIT_TARGET = 0.1

    # declare predictors
    context.indicators = {
        "rsi_05": {
            "fn": FlexyIndicator(
                fn=_get_rsi,
                fn_kwargs={"period": 5},
                a_p_std=34.13, a_p_mean=50
            ),
            "weight": 1
        },
        "rsi_15": {
            "fn": FlexyIndicator(
                fn=_get_rsi,
                fn_kwargs={"period": 15},
                a_p_std=34.13, a_p_mean=50
            ),
            "weight": 2
        },
        "rsi_60": {
            "fn": FlexyIndicator(
                fn=_get_rsi,
                fn_kwargs={"period": 60},
                a_p_std=34.13, a_p_mean=50
            ),
            "weight": 2
        },
        "centering": {
            "fn": FlexyIndicator(
                fn=_get_centering_force
            ),
            "weight": 4
        }
    }

    context.errors = []

    # For all trading pairs in the poloniex bundle, the default denomination
    # currently supported by Catalyst is 1/1000th of a full coin. Use this
    # constant to scale the price of up to that of a full coin if desired.
    context.TICK_SIZE = 1000.0
    pass


def _get_rsi(context, data, period):
    # === get RSI suggestion
    # RSI > 50 means buy
    # RSI < 50 means sell
    # RSI pressure is > 0 if buy suggested, < 0 if sell suggested
    # bounded [0, 100]
    freq = get_environment('data_frequency')
    if freq == 'daily':
        rsi_freq = '1D'
    elif freq == 'minute':
        rsi_freq = '1m'
    else:
        raise ValueError('unknown data_freq "{}"'.format(freq))
    prices = data.history(
        context.asset,
        fields='price',
        bar_count=period*3,  # TODO: what value should this be?
        frequency=rsi_freq
    )
    return talib.RSI(prices.values, timeperiod=period)[-1]


def _get_centering_force(context, data):
    price = data.current(context.asset, 'price')
    cash = context.portfolio.cash

    n_coins = context.portfolio.positions[context.asset].amount
    # n coins * BTC/coin = asset_value (in BTC)
    asset_value = n_coins * price
    portfolio_value = asset_value + cash

    percent_asset = asset_value / portfolio_value
    # === center-forcing towards target position percent
    position_distance = context.TARGET_POSITION_PERCENT - percent_asset*100
    # max_acceptable_distance = min(
    #     context.TARGET_POSITION_PERCENT,
    #     100.0 - context.TARGET_POSITION_PERCENT
    # ) / 100.0
    max_acceptable_distance = 50
    return position_distance / max_acceptable_distance


def _handle_data(context, data):
    price = data.current(context.asset, 'price')
    n_coins = context.portfolio.positions[context.asset].amount
    asset_value = n_coins * price
    cash = context.portfolio.cash
    portfolio_value = asset_value + cash
    percent_asset = asset_value / portfolio_value

    # === weighted sum forces of all suggestions
    # all forces should be bounded [-1, 1]
    weights = []
    forces_arry = []
    names = []
    forces = {}
    for key in context.indicators.keys():
        names.append(key)
        raw_force = context.indicators[key]["fn"].get_value(context, data)
        forces_arry.append(raw_force)
        forces[key] = raw_force  # TODO: should this be * weight
        weights.append(context.indicators[key]["weight"])
    net_force = numpy.average(forces_arry, weights=weights)
    amount_to_buy = net_force * context.MAX_TRADE  # portfolio_value / price

    if context.MIN_TRADE < abs(amount_to_buy):
        print("netforce: " + str(net_force))
        print("\tsubforces: ")
        for i, name in enumerate(names):
            print("\t\t{: >9s}:{:d}(x){:+f}".format(
                name, weights[i], forces[name]
            ))
        try_buy(context, data, amount_to_buy)
    else:
        amount_to_buy = 0
        pass
        # print("meh")
    # is_sell = False
    # is_buy = False
    # # log.info('base currency available: {cash}'.format(cash=cash))
    # # TODO: wait for open orders to fill:
    # # orders = context.blotter.open_orders
    # # if orders:
    # #     log.info('skipping bar until all open orders execute')
    # #     return
    #
    # # TODO: what is all this about?
    # #
    # # is_buy = False
    # # cost_basis = None
    # # if context.asset in context.portfolio.positions:
    # #     position = context.portfolio.positions[context.asset]
    # #
    # #     cost_basis = position.cost_basis
    # #     log.info(
    # #         'found {amount} positions with cost basis {cost_basis}'.format(
    # #             amount=position.amount,
    # #             cost_basis=cost_basis
    # #         )
    # #     )
    # #
    # #     if position.amount >= context.TARGET_POSITIONS:
    # #         log.info(
    # #             'reached positions target: {}'.format(position.amount)
    # #         )
    # #         return
    # #
    # #     if price < cost_basis:
    # #         is_buy = True
    # #     elif (
    # #         position.amount > 0 and
    # #         price > cost_basis * (1 + context.PROFIT_TARGET)
    # #     ):
    # #         profit = (
    # #             (price * position.amount)-(cost_basis * position.amount)
    # #         )
    # #         log.info('closing position, taking profit: {}'.format(profit))
    # #         order_target_percent(
    # #             asset=context.asset,
    # #             target=0,
    # #             limit_price=price * (1 - context.SLIPPAGE_ALLOWED),
    # #         )
    # #     else:
    # #         log.info('no buy or sell opportunity found')
    # # else:
    # #     is_buy = True
    # if is_buy:
    #     try_buy(context, data, buy_increment)
    # if is_sell:
    #     try_buy(context, data, -sell_increment)
    record(
        price=price,
        forces=forces,
        cash=cash,
        volume=data.current(context.asset, 'volume'),
        starting_cash=context.portfolio.starting_cash,
        positions_asset=asset_value,
        percent_asset=percent_asset,
        leverage=context.account.leverage,
        net_force=net_force,
        amount_to_buy=amount_to_buy,
    )


def try_buy(context, data, increment):
    """Attempt a buy/sell.
    Returns false if assets or cash insufficient.
    Returns true if order is successfully placed.
    """
    is_buy = increment > 0
    is_sell = increment < 0
    price = data.current(context.asset, 'price')
    if is_buy:
        if price * increment > context.portfolio.cash:
            log.info('not enough base currency buy')
            return False
        #
        # log.info(
        #     'buying position cheaper than cost basis {} < {}'.format(
        #         price,
        #         'NA'
        #         # cost_basis
        #     )
        # )
        order(
            asset=context.asset,
            amount=increment,
            limit_price=price * (1 + context.SLIPPAGE_ALLOWED)
        )
        return True
    elif is_sell:
        if (
            price * increment >
            context.portfolio.positions[context.asset].amount
        ):
            log.info('not enough asset to sell')
            return False

        order(
            asset=context.asset,
            amount=increment,
            limit_price=price * (1 - context.SLIPPAGE_ALLOWED)
        )
        return True


def _hand_data_dumb(context, data):
    """Stupid always-buy for testing purposes only"""
    price = data.current(context.asset, 'price')
    cash = context.portfolio.cash
    try_buy(
        context, data, context.MIN_TRADE,
    )
    record(
        price=price,
        cash=cash,
        volume=data.current(context.asset, 'volume'),
        starting_cash=context.portfolio.starting_cash,
        leverage=context.account.leverage,
        positions_asset=context.portfolio.positions[context.asset].amount,
    )


def handle_data(context, data):
    # log.info('handling bar {}'.format(data.current_dt))
    # try:
    _handle_data(context, data)
    # except Exception as e:
    #     log.warn('aborting the bar on error {}'.format(e))
    #     context.errors.append(e)
    # log.info('completed bar {}, total execution errors {}'.format(
    #     data.current_dt,
    #     len(context.errors)
    # ))
    # if len(context.errors) > 0:
    #     log.info('the errors:\n{}'.format(context.errors))


if __name__ == '__main__':
    # === long:
    # t0 = pd.to_datetime('2018-09-01', utc=True)
    # tf = pd.to_datetime('2018-12-30', utc=True)
    # === short
    t0 = pd.to_datetime('2018-12-21', utc=True)
    tf = pd.to_datetime('2018-12-22', utc=True)

    run_algorithm(
        live=False,  # set this to true to lose all your money
        capital_base=1,  # starting captial
        data_frequency='minute',  # minute || daily
        initialize=initialize,
        handle_data=handle_data,
        analyze=analyze,
        exchange_name='binance',
        algo_namespace=ALGO_NAMESPACE,
        quote_currency='btc',
        start=t0,
        end=tf,
    )
