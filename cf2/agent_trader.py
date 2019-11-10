"""
usage : python ./cf2/agent_trader.py

to explore the result see analyze.custom.analyze in analyze/custom.py
"""

from logbook import Logger
from catalyst.api import order_target_percent
from catalyst.api import symbol
from catalyst.api import record
from catalyst.api import order
from catalyst.utils.run_algo import run_algorithm
import pandas as pd
import numpy

from indicators.centering import get_centering_force
from indicators.mavg import get_mavg
from indicators.rsi import get_rsi
from analyze.custom import analyze
from FlexyIndicator import FlexyIndicator

ALGO_NAMESPACE = 'agent_based_trader'
log = Logger('Multiple Agent-Based Trading Alg')
WINDOW = 360


def initialize(context):
    log.info('initializing algo')
    context.ASSET_NAME = 'eth_btc'
    context.asset = symbol(context.ASSET_NAME)
    context.i = 0
    context.buys = []
    context.sells = []
    context.hidden_sells = []
    # === alrgorithm calculation settings
    # === buy/sell order settings
    # TODO: scale these according to portfolio balance
    context.MIN_TRADE = 0.1  # [eth]
    context.MAX_TRADE = 1.0  # [eth]
    context.SLIPPAGE_ALLOWED = 0.02  # [% of current price]

    context.TARGET_POSITION_PERCENT = 40.0
    context.MAX_TARGET_DEVIATION = 40.0

    context.PROFIT_TARGET = 0.001  # [% of current price]
    context.UNDER_ESTIMATION = 0.30  # % sold below statistical value

    # declare predictors
    context.indicators = {
        "centering": {
            "fn": FlexyIndicator(
                fn=get_centering_force,
            ),
            "weight": 4
        },
    }
    for n in [0.5, 1, 2]:
        if n == 1:
            weight = 4
        else:
            weight = 1
        w = round(WINDOW*n)
        context.indicators["rsi_"+str(w)] = {
            "fn": FlexyIndicator(
                fn=get_rsi,
                fn_kwargs={"period": w},
                a_p_std=34.13, a_p_mean=50
            ),
            "weight": weight/2
        }
        context.indicators["mva_"+str(w)] = {
            "fn": FlexyIndicator(
                fn=get_mavg,
                fn_kwargs={"window": w},
            ),
            "weight": weight
        }

    context.errors = []

    # For all trading pairs in the poloniex bundle, the default denomination
    # currently supported by Catalyst is 1/1000th of a full coin. Use this
    # constant to scale the price of up to that of a full coin if desired.
    context.TICK_SIZE = 1000.0


def _handle_data(context, data):
    price = data.current(context.asset, 'price')
    n_coins = context.portfolio.positions[context.asset].amount
    asset_value = n_coins * price
    cash = context.portfolio.cash
    portfolio_value = asset_value + cash
    percent_asset = asset_value / portfolio_value

    # === weighted avg forces of all suggestions
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
    amount_to_buy = min(net_force * cash / price, context.MAX_TRADE)
    # log.info('base currency available: {cash}'.format(cash=cash))
    # print("netforce: " + str(net_force))
    # print("\tsubforces: ")
    # for i, name in enumerate(names):
    #     print("\t\t{: >9s}:{:d}(x){:+f}".format(
    #         name, weights[i], forces[name]
    #     ))

    # * when buying, set sell limit @ z-score*-1. ie the positive z-score
    #   opposite from where you bought
    df = data.history(
        context.asset,
        'price',
        bar_count=WINDOW,
        frequency="1m",  # "1T",
    )
    mavg = df.mean()
    amt_below_avg = mavg - price
    # print("{}eth below mavg".format(amt_below_avg))
    profit_target = context.PROFIT_TARGET * price  # in eth

    buy_price = price * (1 + context.SLIPPAGE_ALLOWED)
    sell_price = mavg + amt_below_avg * (1 - context.UNDER_ESTIMATION)
    # wait for open orders to fill:
    if context.i == 1:  # use 1st iteration to initialize to target %
        order_target_percent(
            context.asset, context.TARGET_POSITION_PERCENT/100
        )
        amount_to_buy = 0
    # elif context.i < WINDOW:  # wait
    #     amount_to_buy = 0
    elif len(context.blotter.open_orders) > 0:
        # log.info('skipping bar until all open orders execute')
        # print(context.blotter.open_orders)
        amount_to_buy = 0
        # return
    elif (  # buy
        context.MIN_TRADE < amount_to_buy and
        (sell_price - buy_price) > profit_target
    ):
        amount_to_buy = round(amount_to_buy, 1)
        # TODO:
        # * limit for buying when profit-target is possible
        # * adjust profit-target larger as funding available decreases

        if price * amount_to_buy > context.portfolio.cash:
            print('not enough base currency buy')
        else:
            order(
                asset=context.asset,
                amount=amount_to_buy,
                limit_price=buy_price
            )
            context.buys.append(buy_price)

            # immediately set sell order at opposing z-score
            # hidden sells activated when price approaches sell_price
            context.hidden_sells.append(
                [sell_price, amount_to_buy]
            )
            # sorted by price
            context.hidden_sells.sort(
                key=lambda x: x[0]
            )

            print('buy {:0.4f}{} @{} to sell @{}'.format(
                amount_to_buy, context.ASSET_NAME.split('_')[0],
                buy_price, sell_price
            ))
    elif(
        len(context.hidden_sells) > 0 and
        price > context.hidden_sells[0][0]
    ):
        sell_price, amount_to_sell = context.hidden_sells.pop(0)
        order(
            asset=context.asset,
            amount=-amount_to_sell,
            limit_price=sell_price
        )
        context.sells.append(sell_price)
        print('selling {:0.4f}{}'.format(
            amount_to_sell, context.ASSET_NAME.split('_')[0],
        ))
    else:
        # print((
        #     "no sells | no buys\n" +
        #     "buy {} !> {}\t&&\n" +
        #     "profit {} !> {}"
        # ).format(
        #     amount_to_buy, context.MIN_TRADE,
        #     amt_below_avg*2, profit_target
        # ))
        amount_to_buy = 0

    # # TODO: what is all this about?
    # #
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
    #         log.info(
    #             'reached positions target: {}'.format(position.amount)
    #         )
    #         return
    #
    #     if price < cost_basis:
    #         is_buy = True
    #     elif (
    #         position.amount > 0 and
    #         price > cost_basis * (1 + context.PROFIT_TARGET)
    #     ):
    #         profit = (
    #             (price * position.amount)-(cost_basis * position.amount)
    #         )
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


def handle_data(context, data):
    context.i += 1
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
    # === v-long bear
    # t0 = pd.to_datetime('2018-06-01', utc=True)
    # tf = pd.to_datetime('2018-12-30', utc=True)
    # === long neutral hill
    t0 = pd.to_datetime('2018-01-08', utc=True)
    tf = pd.to_datetime('2018-03-13', utc=True)
    # === med bull
    # t0 = pd.to_datetime('2018-12-21', utc=True)
    # tf = pd.to_datetime('2018-12-30', utc=True)
    # === short neutral
    # t0 = pd.to_datetime('2018-12-21', utc=True)
    # tf = pd.to_datetime('2018-12-21', utc=True)

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
