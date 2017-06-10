"""
cross-correlations and partial cross-correlations
"""

import matplotlib.pyplot as plt
import statsmodels.api as sm

def plotCCF(dta, exog, saveFigPath, **kwargs):
    zoomLagView = 120   # max lag of interest (for zoomed view)

    kwargs.setdefault('marker', 'o')
    kwargs.setdefault('markersize', 5)
    kwargs.setdefault('linestyle', 'None')

    fig = plt.figure(figsize=(12,8))
    ax1=fig.add_subplot(211)

    ax1.set_ylabel('CCF')
    ax1.set_xlabel('lag')
    # print dta

    print("plotting CCF...")
    print('SIZES:',len(dta.values.squeeze()), ',', len(exog.values.squeeze()))

    ccf_x = sm.tsa.ccf(dta.values.squeeze(), exog.values.squeeze())
    ax1.plot(range(1,len(ccf_x)+1), ccf_x, **kwargs)

    ax2=fig.add_subplot(212)
    ax2.plot(range(1,zoomLagView+1), ccf_x[:zoomLagView], **kwargs)

    if (saveFigPath==None):
        plt.show()
    else:
        plt.savefig(str(saveFigPath), bbox_inches='tight')
