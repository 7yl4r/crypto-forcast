from catalyst.api import get_environment
import talib


def get_rsi(context, data, period):
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
