"""
calculates & plots Cross-Correlation Function with trends data as
exogeneous inflow & price as the outflow
"""

import luigi
import pandas
import matplotlib.pyplot as plt
import pickle

import config
from IngestGoogleTrends import IngestGoogleTrends
from preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated
from model.models import fitARIMAX


class ARIMAX_Trends2Price(luigi.Task):

    def requires(self):
        return [
            IngestGoogleTrends(),
            Resample2DailyInterpolated()
        ]

    def output(self):
        return luigi.LocalTarget(config.data_dir + "ARIMAX_Trends2Price.pickle")

    def run(self):
        trends_dta = pandas.read_csv(self.input()[0].path, names=['date','trends'], header=None)
        price_dta  = pandas.read_csv(self.input()[1].path, names=['date','price'], header=None)

        merged_inner = pandas.merge(
            left=trends_dta, left_on='date',
            right=price_dta, right_on='date'
        )

        merged_inner['date'] = pandas.to_datetime(merged_inner['date'])
        merged_inner = merged_inner.set_index('date')

        print(merged_inner['price'])

        model = fitARIMAX(
            merged_inner['price'].astype('float64') ,
            merged_inner['trends'].astype('float64')
        )

        # # print arma_mod20.aic, arma_mod20.bic, arma_mod20.hqic
        print('=== MODEL PARAMS ===')
        print(model.params)

        print('AIC, BIC, HQIC:')
        print(model.aic, model.bic, model.hqic)

        pickle.dump(model, self.output().path)

        # TODO:
        testModelFit(model, ???, ???)
        testDynamicPrediction(model, ???, ???, ???)


def testModelFit(arma_mod30, dta, pid):
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

    plt.savefig(FIG_DIR+'residualsVsTime'+str(pid)+'.png', bbox_inches='tight')
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
    plt.savefig(FIG_DIR+'residualsNormality'+str(pid)+'.png', bbox_inches='tight')

    # plot ACF/PACF for residuals
    plotACFAndPACF(residuals, 'residualsACFAndPACF'+str(pid)+'.png')

    r,q,p = sm.tsa.acf(residuals.values.squeeze(), qstat=True)
    data = np.c_[range(1,41), r[1:], q, p]
    table = pandas.DataFrame(data, columns=['lag', "AC", "Q", "Prob(>Q)"])
    # print table.set_index('lag')

    # sample data indicates a lack of fit.

def testDynamicPrediction(arma_mod30, dta, interven, pid):
    tf = len(dta)
    t0 = tf*2/3
    predict_sunspots = arma_mod30.predict(t0, tf, exog=interven, dynamic=True)
    # print predict_sunspots

    ax = dta.ix['2012':].plot(figsize=(12,8))
    ax = predict_sunspots.plot(ax=ax, style='r--', label='Dynamic Prediction');
    ax.legend();
    # ax.axis((-20.0, 38.0, -4.0, 200.0));
    plt.savefig(FIG_DIR+'dynamicPrediction'+str(pid)+'.png', bbox_inches='tight')

    def mean_forecast_err(y, yhat):
        return y.sub(yhat).mean()

    # mf_err = mean_forecast_err(dta.SUNACTIVITY, predict_sunspots)

    # print ('mean forcast err: ' + str(mf_err))
