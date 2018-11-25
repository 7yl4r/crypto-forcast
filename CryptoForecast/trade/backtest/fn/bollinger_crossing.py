"""
example trading function.
* all contextual data provided as kwargs.
* called at unknown time and should retain no state.
* determines a long/short/none position based on given historical info
    at call time and returns that position.
* buy/sell position is (-) for sell (+) for buy in units of the exchange
    currency.

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


def bollinger_crossing(
    *args,
    price, bollinger_lower, bollinger_upper,
    **kwargs
):
    tradeAmount = config.tradeAmount

    if (price <= bollinger_lower):
        return tradeAmount
    elif (price >= bollinger_upper):
        return -tradeAmount
    else:
        return 0
