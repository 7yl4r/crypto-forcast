import config


class Wallet(object):
    def __init__(self):
        self.assets = {
            'btc': config.assets['btc'],
            'eth': config.assets['eth'],
        }

    def asset_dict(self):
        return self.assets

    def trade(self, selling, buying):
        if min(selling.values()) < 0:
            assert min(buying.values()) < 0
            for coin, amt in selling.items():
                selling[coin] = -amt
            for coin, amt in buying.items():
                buying[coin] = -amt
            return self.trade(buying, selling)

        print("trade {} for {}".format(selling, buying))
        for coin, amt in selling.items():
            if amt > self.assets[coin]:
                print("WARN: insufficient funds")
                return
            self.assets[coin] -= amt

        for coin, amt in buying.items():
            self.assets[coin] += amt

        self._check()

    def _check(self):
        for coin, amt in self.assets.items():
            assert amt >= 0
