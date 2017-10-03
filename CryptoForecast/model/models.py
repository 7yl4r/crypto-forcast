"""
general helper functions for fitting models to data
"""

import statsmodels.api as sm
import pandas

def fitARIMAX(dta, exogeneous):
    # NOTE: can set exog=[] to set exogeneous variables
    print("fitting arimax model...")
    print('dta', dta.shape, ' exog ', exogeneous.shape)
    # model20 = sm.tsa.ARMA(dta, (2,0), exog=interven)
    # arma_mod20 = model20.fit()
    # print arma_mod20.params

    # sm.tsa.ARIMA(dta, (1,0,0), exog=exogeneous)
    arima_model = sm.tsa.statespace.SARIMAX(
        dta,
        order=(7,2,3),
        trend='c',
        exog=exogeneous
    )
    arima_model_result = arima_model.fit(disp=False)
    # # print arma_mod20.aic, arma_mod20.bic, arma_mod20.hqic
    # print '=== MODEL PARAMS ==='
    # print arma_mod30.params
    #
    # print 'AIC, BIC, HQIC:'
    # print arma_mod30.aic, arma_mod30.bic, arma_mod30.hqic

    return arima_model_result
