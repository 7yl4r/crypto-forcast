import talib
import pandas as pd
from logbook import Logger

from catalyst.api import order
# from catalyst.api import order_target_percent
from catalyst.api import symbol
from catalyst.api import record
from catalyst.api import get_environment
from catalyst.utils.run_algo import run_algorithm

from analyze.custom import analyze

ALGO_NAMESPACE = 'buy_the_dip_live'
log = Logger('buy low sell high')


def initialize(context):
    log.info('initializing algo')
    context.ASSET_NAME = 'eth_btc'
    context.asset = symbol(context.ASSET_NAME)

    # === alrgorithm calculation settings
    # TODO: scale these according to portfolio balance
    context.TIMEPERIODS = [2, 10, 100, 1000]
    context.RSI_SWING = 30  # how far on either side of RSI 50 before buy/sell

    # === buy/sell order settings
    # TODO: scale these according to portfolio balance
    context.MIN_TRADE = 0.1
    context.MAX_BUY = 0.5
    context.MAX_SELL = context.MAX_BUY
    context.SLIPPAGE_ALLOWED = 0.02

    # NOTE: I don't kwow what these are and what they do:
    context.TARGET_POSITIONS = 30
    context.PROFIT_TARGET = 0.1

    context.errors = []

    # For all trading pairs in the poloniex bundle, the default denomination
    # currently supported by Catalyst is 1/1000th of a full coin. Use this
    # constant to scale the price of up to that of a full coin if desired.
    context.TICK_SIZE = 1000.0

    pass


def get_rsi(context, data):
    freq = get_environment('data_frequency')
    if freq == 'daily':
        rsi_freq = '1D'
    elif freq == 'minute':
        rsi_freq = '1m'
    else:
        raise ValueError('unknown data_freq "{}"'.format(freq))

    # Relative Strength Index (RSI)
    rsis = []
    for time_period in context.TIMEPERIODS:
        prices = data.history(
            context.asset,
            fields='price',
            bar_count=time_period*3,  # TODO: what value should this be?
            frequency=rsi_freq
        )
        rsis.append(talib.RSI(prices.values, timeperiod=time_period)[-1])
        # log.debug('got rsi: {}'.format(rsi))

    return rsis


def _handle_data(context, data):
    price = data.current(context.asset, 'price')
    cash = context.portfolio.cash
    rsis = get_rsi(context, data)
    is_sell = False
    is_buy = False
    # TODO: for each rsi in rsis do... something?
    rsi = rsis[1]
    # linear scale buy based on distance RSI from 50%
    if rsi < 50 - context.RSI_SWING:  # buy
        is_buy = True
        buy_increment = round(
            context.MIN_TRADE + context.MAX_BUY * (50.0 - rsi) / 50.0, 1
        )
        assert buy_increment > 0
        log.debug("BUY {}".format(buy_increment))
    elif rsi > 50 + context.RSI_SWING:  # sell
        is_sell = True
        sell_increment = round(
            context.MIN_TRADE + context.MAX_SELL * (rsi - 50.0) / 50.0, 1
        )
        assert sell_increment > 0
        log.debug("SELL! {}".format(sell_increment))
    else:
        pass
        # log.debug('rsi is ~50%')

    # log.info('base currency available: {cash}'.format(cash=cash))
    # TODO: wait for open orders to fill:
    # orders = context.blotter.open_orders
    # if orders:
    #     log.info('skipping bar until all open orders execute')
    #     return

    # TODO: what is all this about?
    #
    # is_buy = False
    # cost_basis = None
    # if context.asset in context.portfolio.positions:
    #     position = context.portfolio.positions[context.asset]
    #
    #     cost_basis = position.cost_basis
    #     log.info(
    #         'found {amount} positions with cost basis {cost_basis}'.format(
    #             amount=position.amount,
    #             cost_basis=cost_basis
    #         )
    #     )
    #
    #     if position.amount >= context.TARGET_POSITIONS:
    #         log.info('reached positions target: {}'.format(position.amount))
    #         return
    #
    #     if price < cost_basis:
    #         is_buy = True
    #     elif (
    #         position.amount > 0 and
    #         price > cost_basis * (1 + context.PROFIT_TARGET)
    #     ):
    #         profit = (price * position.amount)-(cost_basis * position.amount)
    #         log.info('closing position, taking profit: {}'.format(profit))
    #         order_target_percent(
    #             asset=context.asset,
    #             target=0,
    #             limit_price=price * (1 - context.SLIPPAGE_ALLOWED),
    #         )
    #     else:
    #         log.info('no buy or sell opportunity found')
    # else:
    #     is_buy = True
    if is_buy:
        try_buy(context, data, buy_increment)
    if is_sell:
        try_buy(context, data, -sell_increment)
    asset_value = context.portfolio.positions[context.asset].amount / price
    record(
        price=price,
        rsi_2=rsis[0],  # TODO: be more clever here
        rsi_4=rsis[1],
        rsi_8=rsis[2],
        rsi_16=rsis[3],
        cash=cash,
        volume=data.current(context.asset, 'volume'),
        starting_cash=context.portfolio.starting_cash,
        positions_asset=asset_value,
        percent_asset=asset_value / (asset_value + cash),
        leverage=context.account.leverage,
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
        # if buy_increment is None:
        #     log.info('the rsi is too high to consider buying {}'.format(rsi))
        #     return
        #
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
    rsi = get_rsi(context, data)
    try_buy(
        context, data, context.MIN_TRADE,
    )
    record(
        price=price,
        rsi=rsi,
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
        start=pd.to_datetime('2018-12-22', utc=True),
        end=pd.to_datetime('2018-12-23', utc=True),
    )
