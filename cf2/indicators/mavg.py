from catalyst.api import get_environment


def get_mavg(context, data, window=10):
    freq = get_environment('data_frequency')
    assert freq == 'minute'

    # Compute moving averages calling data.history() for each
    # moving average with the appropriate parameters. We choose to use
    # minute bars for this simulation -> freq="1m"
    # Returns a pandas dataframe.
    df = data.history(
        context.asset,
        'price',
        bar_count=window,
        frequency="1m",  # "1T",
    )
    mavg = df.mean()
    mstd = df.std()
    # price = data.current(context.asset, 'price')
    price = df[-1]  # data.current(context.asset, 'price')
    zscore = (mavg - price) / mstd
    # print("{} - {} = {}".format(price, mavg, diff))
    return zscore/8.0
