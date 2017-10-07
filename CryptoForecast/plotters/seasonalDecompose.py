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

    ax1 = plt.subplot(411)
    plt.plot(data)#, label='Original')
    ax1.set_title('original')
    plt.legend(loc='best')
    ax2 = plt.subplot(412)
    plt.plot(trend)#, label='Trend')
    ax2.set_title('trend')
    plt.legend(loc='best')
    ax3 = plt.subplot(413)
    plt.plot(seasonal,label=str(decompfreq))
    ax3.set_title('seasonality')
    plt.legend(loc='best')
    ax4 = plt.subplot(414)
    plt.plot(residual)#, label='Residuals')
    ax4.set_title('residuals')
    plt.legend(loc='best')
    plt.tight_layout()
    if (saveFigName == None):
        plt.show()
    else:
        plt.savefig(str(saveFigName))
