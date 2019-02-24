
def get_centering_force(context, data):
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
    max_acceptable_distance = context.MAX_TARGET_DEVIATION
    return position_distance / max_acceptable_distance
