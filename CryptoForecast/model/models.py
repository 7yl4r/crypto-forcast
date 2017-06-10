"""
general helper functions for fitting models to data
"""

import statsmodels.api as sm

def fitARIMAX(dta, exogeneous):
    # NOTE: can set exog=[] to set exogeneous variables
    # model20 = sm.tsa.ARMA(dta, (2,0), exog=interven)
    # arma_mod20 = model20.fit()
    # print arma_mod20.params

    print("fitting arimax model...")
    model30 = sm.tsa.ARMA(dta, (1,0,0), exog=exogeneous)
    arma_mod30 = model30.fit()
    # # print arma_mod20.aic, arma_mod20.bic, arma_mod20.hqic
    # print '=== MODEL PARAMS ==='
    # print arma_mod30.params
    #
    # print 'AIC, BIC, HQIC:'
    # print arma_mod30.aic, arma_mod30.bic, arma_mod30.hqic

    return arma_mod30
