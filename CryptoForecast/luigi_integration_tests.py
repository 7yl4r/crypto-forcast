import luigi
import sys

try:  # py 3.4+
    from unittest.mock import patch
except ImportError:
    from mock import patch

from btc.preprocess.PlotRawData import PlotRawData
from eth.preprocess.PlotRawData import PlotRawDataETH


def create_luigi_task_tst(test_task):
    """
    Helper function tests luigi tasks using PlotRawData.
    Honestly seems kind of silly to mock sys.argv,
    but I don't see any docs for how to run luigi tasks from python
    and this is better than subprocess.call at least.
    """
    testargs = ["prog_name", test_task.__name__]
    with patch.object(sys, 'argv', testargs):
        luigi.run()


def test_btc_plot():
    create_luigi_task_tst(PlotRawData)

## TODO: figure out how to add more tests w/o getting
##      `PidLockAlreadyTakenExit`
# def test_eth_plot():
#     create_luigi_task_tst(PlotRawDataETH)
