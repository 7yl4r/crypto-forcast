"""
calculates & plots Cross-Correlation Function with trends data as
exogeneous inflow & price as the outflow
"""

import luigi
import pandas
import matplotlib.pyplot as plt
import pickle

import statsmodels.api as sm
from scipy import stats
from statsmodels.graphics.api import qqplot
import numpy as np

import config
from preprocess.TrendsInterpolation import TrendsInterpolation
from preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated
from model.models import fitARIMAX

import pdb

class ARIMAX_Trends2Price(luigi.Task):

    def requires(self):
        return [
            TrendsInterpolation(),
            Resample2DailyInterpolated()
        ]

    def output(self):
        # return luigi.LocalTarget(config.data_dir + "ARIMAX_Trends2Price.pickle")
        return luigi.LocalTarget(config.plot_dir + 'ARIMAX_test_dynamicPrediction.png')

    def run(self):
        trends_dta = pandas.read_csv(self.input()[0].path, names=['date','trends'], header=0)
        price_dta  = pandas.read_csv(self.input()[1].path, names=['date','price'], header=0)

        merged_inner = pandas.merge(
            left=trends_dta, left_on='date',
            right=price_dta, right_on='date'
        )

        # merged_inner['date'] = pandas.to_datetime(merged_inner['date'])
        merged_inner = merged_inner.set_index('date')

        # home:
        # how to apply dateutil parser to all values in column
        #   df['date'].apply(dateutil.parser.parse)

        # print(merged_inner['price'])
        endog = merged_inner['price'].astype('float64')
        exog = merged_inner['trends'].astype('float64')
        print('endog: ', endog)
        print('exog: ', exog)

        model = fitARIMAX(
            endog,
            exog
        )

        # # print arma_mod20.aic, arma_mod20.bic, arma_mod20.hqic
        print('=== MODEL PARAMS ===')
        print(model.params,'\n')

        print('AIC, BIC, HQIC:')
        print(model.aic, model.bic, model.hqic, '\n')

        # with open(self.output().path, 'wb') as outfile:
        #     pickle.dump(model, outfile)

        # TODO: use self.output() for these figures too
        testModelFit(model, endog)
        print(merged_inner)
        testDynamicPrediction(model, endog, exog)


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

    plt.savefig(config.plot_dir + 'ARIMAX_test_residualsVsTime.png', bbox_inches='tight')
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
    plt.savefig(config.plot_dir + 'ARIMAX_test_residualsNormality.png', bbox_inches='tight')

    plt.clf()
    # plot ACF/PACF for residuals
    plotACFAndPACF(residuals, 'residualsACFAndPACF.png')

    r,q,p = sm.tsa.acf(residuals.values.squeeze(), qstat=True)
    data = np.c_[range(1,41), r[1:], q, p]
    table = pandas.DataFrame(data, columns=['lag', "AC", "Q", "Prob(>Q)"])
    print(table.set_index('lag'))

    # sample data indicates a lack of fit.

def testDynamicPrediction(arma_mod30, dta, interven):
    latest   = dta.index[-1]
    earliest = dta.index[0]
    # range_delta = latest - earliest
    tf = '2017-10-30' #  #len(dta)
    t0 = '2016-01-01'

    # print(interven)

    print('==========================================================')
    print('earliest', '\t\t', 't0     ', '\t\t', 'tf    ', '\t\t', 'latest')
    print(earliest,   '\t\t',  t0,       '\t\t',  tf,      '\t\t',  latest)
    print('==========================================================')

    # print(arma_mod30)
    # print(dir(arma_mod30))

    predict_sunspots = arma_mod30.predict(t0, tf, exog=interven, dynamic=True)
    # print predict_sunspots

    selected_dta = dta.loc[t0:]
    print('selected_dta: \n', selected_dta)
    ax = selected_dta.plot(figsize=(12,8))
    # ax = dta.plot()
    plt.savefig(config.plot_dir + "ARIMAX_test_dynamicPrediction_pre.png", bbox_inches='tight')


    # this crashes next part crashes...
    print("\n\npredictions:\n", predict_sunspots)
    ax = predict_sunspots.plot(ax=ax, style='r--', label='Dynamic Prediction', figsize=(12,8));
    # ax.legend();
    # ax.axis((-20.0, 38.0, -4.0, 200.0));
    plt.savefig(config.plot_dir + 'ARIMAX_test_dynamicPrediction.png', bbox_inches='tight')

    plt.clf()

    def mean_forecast_err(y, yhat):
        return y.sub(yhat).mean()

    # mf_err = mean_forecast_err(dta.SUNACTIVITY, predict_sunspots)

    # print ('mean forcast err: ' + str(mf_err))


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
        plt.savefig(config.plot_dir+str(saveFigName), bbox_inches='tight')
    plt.clf()
