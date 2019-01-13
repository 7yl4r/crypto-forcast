import talib
import pandas as pd
from logbook import Logger

from catalyst.api import order
# from catalyst.api import order_target_percent
from catalyst.api import symbol
from catalyst.api import record
from catalyst.utils.run_algo import run_algorithm

from analyze.dual_ma import analyze

ALGO_NAMESPACE = 'buy_the_dip_live'
log = Logger('buy low sell high')


def initialize(context):
    log.info('initializing algo')
    context.ASSET_NAME = 'eth_btc'
    context.asset = symbol(context.ASSET_NAME)

    context.TARGET_POSITIONS = 30
    context.PROFIT_TARGET = 0.1
    context.SLIPPAGE_ALLOWED = 0.02

    context.errors = []
    pass


def _handle_data(context, data):
    price = data.current(context.asset, 'price')
    log.info('got price {price}'.format(price=price))

    prices = data.history(
        context.asset,
        fields='price',
        bar_count=20,
        frequency='1D'
    )
    # Relative Strength Index (RSI)
    rsi = talib.RSI(prices.values, timeperiod=14)[-1]
    log.info('got rsi: {}'.format(rsi))

    # TODO: scale these according to portfolio balance
    RSI_SWING = 30  # how far on either side of RSI 50 before buy/sell
    MIN_TRADE = 0.1
    MAX_BUY = 0.5
    MAX_SELL = MAX_BUY
    is_sell = False
    is_buy = False
    # linear scale buy based on distance RSI from 50%
    if rsi < 50 - RSI_SWING:  # buy
        is_buy = True
        buy_increment = round(MIN_TRADE + MAX_BUY * (50.0 - rsi) / 50.0, 1)
        assert buy_increment > 0
        log.info("BUY {}".format(buy_increment))
    elif rsi > 50 + RSI_SWING:  # sell
        is_sell = True
        sell_increment = round(MIN_TRADE + MAX_SELL * (rsi - 50.0) / 50.0, 1)
        assert sell_increment > 0
        log.info("SELL! {}".format(sell_increment))
    else:
        log.info('rsi is ~50%')

    cash = context.portfolio.cash
    log.info('base currency available: {cash}'.format(cash=cash))

    record(
        price=price,
        rsi=rsi,
    )
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
        # if buy_increment is None:
        #     log.info('the rsi is too high to consider buying {}'.format(rsi))
        #     return
        #
        # if price * buy_increment > cash:
        #     log.info('not enough base currency to consider buying')
        #     return
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
            amount=buy_increment,
            limit_price=price * (1 + context.SLIPPAGE_ALLOWED)
        )
    elif is_sell:
        order(
            asset=context.asset,
            amount=-sell_increment,
            limit_price=price * (1 - context.SLIPPAGE_ALLOWED)
        )


def handle_data(context, data):
    log.info('handling bar {}'.format(data.current_dt))
    # try:
    _handle_data(context, data)
    # except Exception as e:
    #     log.warn('aborting the bar on error {}'.format(e))
    #     context.errors.append(e)

    log.info('completed bar {}, total execution errors {}'.format(
        data.current_dt,
        len(context.errors)
    ))

    if len(context.errors) > 0:
        log.info('the errors:\n{}'.format(context.errors))


if __name__ == '__main__':
    live = False
    if live:
        run_algorithm(
            capital_base=10,
            initialize=initialize,
            handle_data=handle_data,
            analyze=analyze,
            exchange_name='bittrex',
            live=True,
            algo_namespace=ALGO_NAMESPACE,
            quote_currency='btc',
            simulate_orders=True,
        )
    else:
        run_algorithm(
            capital_base=1,
            data_frequency='daily',
            initialize=initialize,
            handle_data=handle_data,
            analyze=analyze,
            exchange_name='binance',
            algo_namespace=ALGO_NAMESPACE,
            quote_currency='btc',
            start=pd.to_datetime('2017-07-15', utc=True),
            end=pd.to_datetime('2018-12-23', utc=True),
        )
