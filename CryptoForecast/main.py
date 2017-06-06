#!/usr/bin/env python3
# re-creation of
#   http://statsmodels.sourceforge.net/devel/examples/notebooks/generated/tsa_arma.html

import numpy as np
from scipy import stats
import pandas
import matplotlib.pyplot as plt

import statsmodels.api as sm

from statsmodels.graphics.api import qqplot

FIG_DIR = 'results/'

def loadSampleData():
    print(sm.datasets.sunspots.NOTE)

    dta = sm.datasets.sunspots.load_pandas().data

    dta.index = pandas.Index(sm.tsa.datetools.dates_from_range('1700', '2008'))
    del dta["YEAR"]

    dta.plot(figsize=(12,8))

    plt.savefig(FIG_DIR+'dataView.png', bbox_inches='tight')
    # plt.show()

    return dta

def plotACFAndPACF(dta, saveFigName=None):
    fig = plt.figure(figsize=(12,8))
    ax1 = fig.add_subplot(211)
    # squeeze = Remove single-dimensional entries from the shape of an array.
    # Plots lags on the horizontal and the correlations on vertical axis
    ax1.set_ylabel('correlation')
    ax1.set_xlabel('lag')
    fig = sm.graphics.tsa.plot_acf(dta.values.squeeze(), lags=40, ax=ax1)

    # partial act
    # Plots lags on the horizontal and the correlations on vertical axis
    ax2 = fig.add_subplot(212)
    ax1.set_ylabel('correlation')
    ax1.set_xlabel('lag')
    fig = sm.graphics.tsa.plot_pacf(dta, lags=40, ax=ax2)

    if (saveFigName==None):
        plt.show()
    else:
        plt.savefig(FIG_DIR+str(saveFigName), bbox_inches='tight')

def fitModel(dta):
    # NOTE: can set exog=[] to set exogeneous variables
    model20 = sm.tsa.ARMA(dta, (2,0))
    arma_mod20 = model20.fit()
    print(arma_mod20.params)

    model30 = sm.tsa.ARMA(dta, (3,0))
    arma_mod30 = model30.fit()
    print(arma_mod20.aic, arma_mod20.bic, arma_mod20.hqic)
    print(arma_mod30.params)

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
    predict_sunspots = arma_mod30.predict('1990', '2012', dynamic=True)
    print(predict_sunspots)

    ax = dta.ix['1950':].plot(figsize=(12,8))
    ax = predict_sunspots.plot(ax=ax, style='r--', label='Dynamic Prediction');
    ax.legend();
    ax.axis((-20.0, 38.0, -4.0, 200.0));
    plt.savefig(FIG_DIR+'dynamicPrediction.png', bbox_inches='tight')

    def mean_forecast_err(y, yhat):
        return y.sub(yhat).mean()

    mf_err = mean_forecast_err(dta.SUNACTIVITY, predict_sunspots)

    print ('mean forcast err: ' + str(mf_err))

if __name__ == '__main__':
    dta = loadSampleData()
    plotACFAndPACF(dta, 'acf_and_pacf.png')
    arma_mod30 = fitModel(dta)
    testModelFit(arma_mod30, dta)
    testDynamicPrediction(arma_mod30, dta)
    # more example methods @:
    # Simulated ARMA(4,1): Model Identification is Difficult
