"""
cross-correlations and partial cross-correlations
"""

import matplotlib.pyplot as plt

from statsmodels.tsa.seasonal import seasonal_decompose

import datetime

def seasonalDecompose(data, saveFigName=None, dataResolution=1, seasonLen=60*24):
    """
    seasonLen = 60*24 # expected season length [min]
    dataResolution = 1 # [min]
    """
    decompfreq = int(seasonLen/dataResolution)  # TODO: round this instead...
    print("decomposing w/ frequency f=", decompfreq)
    decomposition = seasonal_decompose(data.values, freq=decompfreq)

    trend = decomposition.trend
    seasonal = decomposition.seasonal
    residual = decomposition.resid

    plt.subplot(411)
    plt.plot(data, label='Original')
    plt.legend(loc='best')
    plt.subplot(412)
    plt.plot(trend, label='Trend')
    plt.legend(loc='best')
    plt.subplot(413)
    plt.plot(seasonal,label='Seasonality')
    plt.legend(loc='best')
    plt.subplot(414)
    plt.plot(residual, label='Residuals')
    plt.legend(loc='best')
    plt.tight_layout()
    if (saveFigName == None):
        plt.show()
    else:
        plt.savefig(str(saveFigName))
