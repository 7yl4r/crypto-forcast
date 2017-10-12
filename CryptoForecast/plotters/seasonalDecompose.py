"""
cross-correlations and partial cross-correlations
"""

import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import datetime
import itertools
import numpy as np
from matplotlib.mlab import griddata
from mpl_toolkits.mplot3d import Axes3D
from pylab import *

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

    plotSeasonBreakdown(data, trend, seasonal, residual, decompfreq, saveFigName)
    # plotRibbons(seasonal, "".join(saveFigName.split('.')[:-1])+"_ribbon.png", seasonLen)
    return trend, seasonal, residual

def plotSeasonBreakdown(data, trend, seasonal, residual, decompfreq, saveFigName=None):
    """ plots each on own subplot """
    ax1 = plt.subplot(411)
    # print(data)
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

def plotImage(dta, saveFigName):
    plt.clf()
    dx, dy = 1, 1
    # generate 2 2d grids for the x & y bounds
    with np.errstate(invalid='ignore'):
        y, x = np.mgrid[
            slice(0, len(dta)   , dx),
            slice(0, len(dta[0]), dy)
        ]
        z = dta
        z_min, z_max = -np.abs(z).max(), np.abs(z).max()

        #try:
        c = plt.pcolormesh(x, y, z, cmap='hsv', vmin=z_min, vmax=z_max)
        #except ??? as err:  # data not regular?
        #   c = plt.pcolor(x, y, z, cmap='hsv', vmin=z_min, vmax=z_max)
        d = plt.colorbar(c, orientation='vertical')
        lx = plt.xlabel("index")
        ly = plt.ylabel("lag")
        plt.savefig(str(saveFigName))

def plotRibbons(dta, saveFigName, index):
    """
    creates ribbon-plot one-ribbon-at-a-time
    """
    fig=gcf()
    ax=fig.gca(projection='3d')
    width=5  # assumes two indicies aren't too close together...
    y_min=0  # assumes given index (season len) is between 0-100
    y_max=100

    y=dta
    x=sorted(list(range(1,len(y)+1))*2)
    a=[index,index+width]*len(y)
    b=list(itertools.chain(*zip(y,y)))
    xi=np.linspace(min(x),max(x))
    yi=np.linspace(min(a),max(a))
    X,Y=np.meshgrid(xi,yi)
    Z=griddata(x,a,b,xi,yi, interp='linear')

    # to plot w/ y-axis colormapped:
    # colors =plt.cm.spectral( (Y-Y.min())/float((Y-Y.min()).max()) )
    colors =plt.cm.spectral( (Y-y_min)/float(y_max-y_min) )
    ax.plot_surface(X,Y,Z ,facecolors=colors, linewidth=0, shade=False )

    # to plot w/ z-axis colormapped:
    # ax.plot_surface(X,Y,Z,rstride=50,cstride=1,cmap='Spectral')

    ax.set_zlim3d(np.min(Z),np.max(Z))
    ax.grid(False)
    ax.w_xaxis.pane.set_visible(False)
    ax.w_yaxis.pane.set_visible(False)
    ax.w_zaxis.pane.set_color('gainsboro')
    # ax.set_title('Molecular spectra')
    # ax.set_xlim3d(0,23)
    # ax.set_xticks([1.6735,6.8367,12.0000,17.1633,22.3265])
    # ax.set_xticklabels(['350','400','450','500','550'])
    # ax.set_xlabel('Wavelength (nm)')
    # ax.set_yticks([0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5])
    # ax.set_yticklabels(['1','2','3','4','5','6','7','8'])
    # ax.set_ylabel('Spectrum')
    # ax.set_zlim3d(0,2)
    # ax.set_zlabel('Absorbance')
    plt.savefig(str(saveFigName))
