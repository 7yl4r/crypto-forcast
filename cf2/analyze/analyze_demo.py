import matplotlib.pyplot as plt
from logbook import Logger

from catalyst.exchange.utils.stats_utils import get_pretty_stats

log = Logger('analyze.demo')


def analyze(context, perf):
    log.info('the daily stats:\n{}'.format(get_pretty_stats(perf)))

    ax1 = plt.subplot(211)
    perf.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel('portfolio value')
    ax2 = plt.subplot(212, sharex=ax1)
    perf.ending_cash.plot(ax=ax2)
    ax2.set_ylabel('ending_cash')
    plt.show()
    # plt.savefig("analysis.png", bbox_inches='tight')
