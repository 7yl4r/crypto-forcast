"""
config:
-------
tradeAmount: amount, in ETH, to trade every time

parameters:
-----------
bollinger_lower :
bollinger_upper :
price :

"""
import config


def bollinger_cross_balanced(
    *args,
    price,
    bollinger_lower, bollinger_upper,
    max_trade,
    eth_btc_ratio,
    **kwargs
):
    IDEAL_RATIO = 1
    if (price <= bollinger_lower):
        return max_trade
    elif (price >= bollinger_upper):
        return -max_trade
    else:
        if eth_btc_ratio > IDEAL_RATIO:
            # too much eth
            return config.tradeAmount
        else:
            # not enough eth
            return -config.tradeAmount
