"""
NOTE: this algorithm not yet implemented.
The code here was copied from multi_inicator_trader.py.

This trading algorithm reads from three timeseries:
    * XMR/ETH
    * XMR/$
    * ETH/$

The idea is that the XMR/ETH pair should match the XMR/$ to ETH/$ ratio.
If the ratios do not match there is an opportunity to compete profitable
trades.

When the $ ratio < pair ratio:
    * XMR under-valued in XMR/$ OR XMR over-valued in XMR/ETH
    * ETH over-valued in ETH/$ OR XMR under-valued in XMR/ETH
    * buy XMR/$
    * ??? XMR/ETH
    * sell ETH/$

When the $ ratio > pair ratio:
    * buy XMR/ETH
    * sell XMR/$
    * buy ETH/$

The buys and sells create a pressure against other pressures.
Example pressures include:
    * centering pressure attempting to balance 50% eth & 50% xmr
    * moving average pressures
    * rsi pressures
"""
from pprint import pprint

from binance.client import Client

from secrets import API_KEY, API_SECRET

TRADE_FEE_PERCENT = 0.075/100
TRADE_INCREMENT = 0.1  # amount to trade in XMR
MINIMUM_TRADE_PROFIT_PERCENT = 0.1


def _load_data():
    # TODO: use pandas dataframes here
    # TODO: load existing data
    return {
        # market prices:
        "XMRUSDT": [],
        "ETHUSDT": [],
        "XMRETH": [],
        # indicies:
        "XMRETH_ratio": [],
    }

def _add_calculated_ratio(data):
    """adds the calculated XMR/ETH ratio to data"""
    tgt = data['XMRUSDT'][-1]
    base = data['ETHUSDT'][-1]
    ratio = float(tgt) / float(base)
    data['XMRETH_ratio'].append(ratio)
    return data


def _xmr_dollar_ratio_lt_pair(client, data, balances):
    # === XMR under-valued in $ market, over-valued in ETH market
    # sell XMR/ETH
    order = client.order_market_sell(
        symbol='XMRETH',
        quantity=TRADE_INCREMENT
    )
    # buy XMR/$
    order = client.order_market_buy(
        symbol='XMRUSDT',
        quantity=TRADE_INCREMENT
    )
    print("sell XMR/ETH && buy XMR/$")


def _xmr_dollar_ratio_gt_pair(client, data, balances):
    # === XMR over-valued in $ market, under-valued in ETH market
    # buy XMR/ETH
    order = client.order_market_buy(
        symbol='XMRETH',
        quantity=TRADE_INCREMENT
    )
    # sell XMR/$
    order = client.order_market_sell(
        symbol='XMRUSDT',
        quantity=TRADE_INCREMENT
    )
    print("sell XMR/$ && buy XMR/ETH")


def get_data():
    client = Client(API_KEY, API_SECRET)

    data = _load_data()
    for symbol in ['XMRETH', 'ETHUSDT', 'XMRUSDT']:
        print("fetching {}".format(symbol))
        data[symbol].append(float(client.get_avg_price(symbol=symbol)['price']))
        print(data[symbol][-1])

    data = _add_calculated_ratio(data)
    print("dollar:eth = {}:{}", data["XMRETH_ratio"], data["XMRETH"])

    balances = {
        "XMR": client.get_asset_balance(asset='XMR', recvWindow=60000)['free'],
        "ETH": client.get_asset_balance(asset='ETH', recvWindow=60000)['free']
    }
    print('balances:')
    pprint(balances)

    imbalance = data['XMRETH_ratio'][-1] - data['XMRETH'][-1]
    imbalance_percent = 100 * imbalance / max(
        data['XMRETH_ratio'][-1], data['XMRETH'][-1]
    )
    print("ratio_imbalance:{} ({}%)".format(imbalance, imbalance_percent))
    # XMRETH*ETH$ - 1XMR$  = $ profit per XMR
    trade_profit = abs(
        data['XMRETH'][-1] * data["ETHUSDT"][-1] - data['XMRUSDT'][-1]
    )
    trade_profit -= (
        TRADE_FEE_PERCENT*data['XMRETH'][-1]*data['ETHUSDT'][-1] +
        TRADE_FEE_PERCENT*data['XMRUSDT'][-1]
    )
    trade_profit_percent = 100 * trade_profit / data['XMRUSDT'][-1]
    print("trade profit = ${} ({}%)".format(
        trade_profit,
        trade_profit_percent
    ))

    action = 'none'
    if trade_profit_percent > MINIMUM_TRADE_PROFIT_PERCENT:
        if data['XMRETH_ratio'][-1] < data['XMRETH'][-1]:
            _xmr_dollar_ratio_lt_pair(client, data, balances)
            action = '$ ratio < pair ratio'
        elif data['XMRETH_ratio'][-1] > data['XMRETH'][-1]:
            _xmr_dollar_ratio_gt_pair(client, data, balances)
            action = '$ ratio > pair ratio'
        else:
            print('no ratio imbalance')  # this should never print
    print(action)
    # with open('imbalance.csv', 'a') as f_obj:
    #     print(imbalance_percent, file=f_obj)
    # with open('profit.csv', 'a') as f_obj:
    #     print(trade_profit_percent, file=f_obj)
    # with open('action.csv', 'a') as f_obj:
    #     print(action, file=f_obj)
    with open('summary.csv', 'a') as f_obj:
        print('{},{},{},{}'.format(
            balances['XMR'],
            action,
            imbalance_percent,
            trade_profit_percent
        ), file=f_obj)

    # TODO: save stuff to file


if __name__ == "__main__":
    get_data()
