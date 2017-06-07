#!/usr/bin/env python3
# NOTE: this file is being ported to luigi jobs;
#       please see the main luigi file run_luigi.py
# re-creation of
#   http://statsmodels.sourceforge.net/devel/examples/notebooks/generated/tsa_arma.html

import numpy as np
from scipy import stats, fftpack
import pandas
import matplotlib.pyplot as plt

import statsmodels.api as sm

from statsmodels.graphics.api import qqplot
from statsmodels.tsa.seasonal import seasonal_decompose

import datetime

FIG_DIR = 'results/'
FIG_SIZE= (12, 8)
BINSIZE = 30 # in minutes

def dateparse (time_in_secs):
    return datetime.datetime.fromtimestamp(float(time_in_secs))

def loadSampleData():
    """ loads sample pandas dataframe of sunspot data"""
    print(sm.datasets.sunspots.NOTE)

    dta = sm.datasets.sunspots.load_pandas().data

    dta.index = pandas.Index(sm.tsa.datetools.dates_from_range('1700', '2008'))
    del dta["YEAR"]

    dta.plot(figsize=FIG_SIZE)

    plt.savefig(FIG_DIR+'dataView.png', bbox_inches='tight')
    # plt.show()

    return dta

def loadSampledata2():
    """
    loads sample pandas dataframe of data from csv
    csv files can be ingested from http://api.bitcoincharts.com/v1/csv/
        these are updated twice daily
    """
    dta = pandas.read_csv(
        'data/coinbaseUSD_sample.csv', usecols=[0,1], index_col=0,
        parse_dates=True, date_parser=dateparse,
        names=['DateTime', 'price']
    )

    # average duplicate indexes
    # NOTE: weighted average using col 2 (trade volume) would be better...
    dta = dta.groupby('DateTime').mean()

    dta.plot(figsize=FIG_SIZE)

    # downsample using mean
    dta.resample(str(BINSIZE)+'T').mean()

    plt.savefig(FIG_DIR+'dataView.png', bbox_inches='tight')

    return dta


def plotACFAndPACF(dta, saveFigName=None):
    LAGS = 60/BINSIZE*24*8 # 8 days no matter what binsize is
    fig = plt.figure(figsize=(12,8))
    ax1 = fig.add_subplot(211)
    # squeeze = Remove single-dimensional entries from the shape of an array.
    # Plots lags on the horizontal and the correlations on vertical axis
    ax1.set_ylabel('correlation')
    ax1.set_xlabel('lag')
    fig = sm.graphics.tsa.plot_acf(dta.values.squeeze(), lags=LAGS, ax=ax1)

    # partial act
    # Plots lags on the horizontal and the correlations on vertical axis
    ax2 = fig.add_subplot(212)
    ax1.set_ylabel('correlation')
    ax1.set_xlabel('lag')
    fig = sm.graphics.tsa.plot_pacf(dta, lags=LAGS, ax=ax2)

    if (saveFigName==None):
        plt.show()
    else:
        plt.savefig(FIG_DIR+str(saveFigName), bbox_inches='tight')

def fitModel(dta, interven=None):
    # NOTE: can set exog=[] to set exogeneous variables
    # model20 = sm.tsa.ARMA(dta, (2,0), exog=interven)
    # arma_mod20 = model20.fit()
    # print arma_mod20.params

    model30 = sm.tsa.ARMA(dta, (3,0))
    # model30 = sm.tsa.ARMA(dta, (1,0,0), exog=interven)
    arma_mod30 = model30.fit()
    # print arma_mod20.aic, arma_mod20.bic, arma_mod20.hqic
    print('=== MODEL PARAMS ===')
    print(arma_mod30.params)

    print('AIC, BIC, HQIC:')
    print(arma_mod30.aic, arma_mod30.bic, arma_mod30.hqic)

    return arma_mod30

def testModelFit(arma_mod30, dta):
    # does our model fit the theory?
    residuals = arma_mod30.resid
    sm.stats.durbin_watson(residuals.values)
    # NOTE: Durbin Watson Test Statistic approximately equal to 2*(1-r)
    #       where r is the sample autocorrelation of the residuals.
    #       Thus, for r == 0, indicating no serial correlation,
    #       the test statistic equals 2. This statistic will always be
    #       between 0 and 4. The closer to 0 the statistic, the more evidence
    #       for positive serial correlation. The closer to 4, the more evidence
    #       for negative serial correlation.

    # plot the residuals so we can see if there are any areas in time which
    # are poorly explained.
    fig = plt.figure(figsize=(12,8))
    ax = fig.add_subplot(111)
    ax = arma_mod30.resid.plot(ax=ax);

    plt.savefig(FIG_DIR+'residualsVsTime.png', bbox_inches='tight')
#    plt.show()

    # tests if samples are different from normal dist.
    k2, p = stats.normaltest(residuals)
    print ("residuals skew (k2):" + str(k2) +
           " fit w/ normal dist (p-value): " + str(p))

    # plot residuals
    fig = plt.figure(figsize=(12,8))
    ax = fig.add_subplot(211)
    fig = qqplot(residuals, line='q', ax=ax, fit=True)

    ax2 = fig.add_subplot(212)
    # resid_dev = residuals.resid_deviance.copy()
    # resid_std = (resid_dev - resid_dev.mean()) / resid_dev.std()
    plt.hist(residuals, bins=25);
    plt.title('Histogram of standardized deviance residuals');
    plt.savefig(FIG_DIR+'residualsNormality.png', bbox_inches='tight')

    # plot ACF/PACF for residuals
    plotACFAndPACF(residuals, 'residualsACFAndPACF.png')

    r,q,p = sm.tsa.acf(residuals.values.squeeze(), qstat=True)
    data = np.c_[range(1,41), r[1:], q, p]
    table = pandas.DataFrame(data, columns=['lag', "AC", "Q", "Prob(>Q)"])
    print(table.set_index('lag'))

    # sameple data indicates a lack of fit.


def testDynamicPrediction(arma_mod30, dta):
    # predict_sunspots = arma_mod30.predict('1990', '2012', dynamic=True)  # for sunspot data
    print('last date: ', dta.index[-1])
    _start = dta.index[-1] - datetime.timedelta(minutes=5)
    _end = dta.index[-1] + datetime.timedelta(minutes=1)
    start = dta.index.get_loc(_start, method='nearest')
    end = dta.index.get_loc(_end, method='nearest')
    print('predict from', start, ' to ', end)
    predict_sunspots = arma_mod30.predict(
        start,
        end,
        dynamic=True
    )  # for btc price data
    # print('prediction: ', predict_sunspots)

    # ax = dta.ix['1950':].plot(figsize=(12,8)) # for sunspot data
    ax = dta.iloc[start:].plot(figsize=FIG_SIZE)  # for btc price
    # print('dta slice: ', dta.iloc[start:])
    ax = predict_sunspots.plot(ax=ax, style='r--', label='Dynamic Prediction');
    ax.legend();
    ax.axis((-20.0, 38.0, -4.0, 200.0));
    plt.savefig(FIG_DIR+'dynamicPrediction.png', bbox_inches='tight')

    def mean_forecast_err(y, yhat):
        return y.sub(yhat).mean()

    mf_err = mean_forecast_err(dta.SUNACTIVITY, predict_sunspots)

    print ('mean forcast err: ' + str(mf_err))

def plotFFT(df):

    # Number of samplepoints
    N = len(df)
    # sample spacing
    T = BINSIZE*60.0
    x = np.linspace(0.0, N*T, N)
    y = df.values #np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
    yf = fftpack.fft(y)
    xf = np.linspace(0.0, 1.0/(2.0*T), N/2)

    fig, ax = plt.subplots()
    ax.plot(xf, 2.0/N * np.abs(yf[:N//2]))
    plt.savefig(FIG_DIR+'fft.png', bbox_inches='tight')

def plot_deriv_fft(df):
    # Number of samplepoints
    N = len(df)
    # sample spacing
    T = BINSIZE*60.0
    x = np.linspace(0.0, N*T, N-1)
    y = [df.values[i]-df.values[i-1] for i in range(1,len(df.values))] #np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
    yf = fftpack.fft(y)
    xf = np.linspace(0.0, 1.0/(2.0*T), N/2)

    fig, ax = plt.subplots()
    ax.plot(x, y)
    plt.savefig(FIG_DIR+'deriv.png', bbox_inches='tight')

    fig, ax = plt.subplots()
    ax.plot(xf, 2.0/N * np.abs(yf[:N//2]))
    plt.savefig(FIG_DIR+'fft_deriv.png', bbox_inches='tight')

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

def plotCCF(dta, exog, saveFigName, **kwargs):
    zoomLagView = 120   # max lag of interest (for zoomed view)

    kwargs.setdefault('marker', 'o')
    kwargs.setdefault('markersize', 5)
    kwargs.setdefault('linestyle', 'None')

    fig = plt.figure(figsize=(12,8))
    ax1=fig.add_subplot(211)

    ax1.set_ylabel('CCF')
    ax1.set_xlabel('lag')
    # print dta

    print('SIZES:',len(dta.values.squeeze()), ',', len(exog.values.squeeze()))

    ccf_x = sm.tsa.ccf(dta.values.squeeze(), exog.values.squeeze())
    ax1.plot(range(1,len(ccf_x)+1), ccf_x, **kwargs)

    ax2=fig.add_subplot(212)
    ax2.plot(range(1,zoomLagView+1), ccf_x[:zoomLagView], **kwargs)

    if (saveFigName==None):
        plt.show()
    else:
        plt.savefig(FIG_DIR+str(saveFigName), bbox_inches='tight')

if __name__ == '__main__':
    dta = loadSampledata2()
    # plotACFAndPACF(dta, 'acf_and_pacf.png')
    arma_mod30 = fitModel(dta)
    testModelFit(arma_mod30, dta)
    # testDynamicPrediction(arma_mod30, dta)

    plotFFT(dta)
    plot_deriv_fft(dta)

    seasonalDecompose(
        dta, saveFigName=FIG_DIR+'seasonal.png', dataResolution=BINSIZE,
        seasonLen=60*24
    )

    # for exog vars:
    #plotCCF(dta, exog, FIG_DIR+'seasonal.png')
