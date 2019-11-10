from catalyst.api import order


def try_buy(context, data, increment):
    """Attempt a buy/sell.
    Returns false if assets or cash insufficient.
    Returns true if order is successfully placed.
    """
    # INCREMENT = 5.0
    is_buy = increment > 0
    is_sell = increment < 0
    price = data.current(context.asset, 'price')
    if is_buy:
        # increment = INCREMENT
        print('buy {:0.4f}{}'.format(
            increment, context.ASSET_NAME.split('_')[0]
        ))
        if price * increment > context.portfolio.cash:
            print('not enough base currency buy')
            return False
        #
        # log.info(
        #     'buying position cheaper than cost basis {} < {}'.format(
        #         price,
        #         'NA'
        #         # cost_basis
        #     )
        # )
        buy_price = price * (1 + context.SLIPPAGE_ALLOWED)
        order(
            asset=context.asset,
            amount=increment,
            limit_price=buy_price
        )
        context.buys.append(buy_price)
        return True
    elif is_sell:
        # increment = -INCREMENT
        print('sell {:0.4f}{}'.format(
            -increment, context.ASSET_NAME.split('_')[0]
        ))
        if (
            abs(increment) >
            context.portfolio.positions[context.asset].amount
        ):
            print('not enough asset to sell')
            return False
        sell_price = price * (1 - context.SLIPPAGE_ALLOWED)
        order(
            asset=context.asset,
            amount=increment,
            limit_price=sell_price
        )
        context.sells.append(sell_price)
        return True
