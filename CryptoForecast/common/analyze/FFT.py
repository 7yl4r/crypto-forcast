"""
creates plot of FFT for data
"""

import luigi
import pandas
import numpy as np
import scipy.fftpack
import matplotlib.pyplot as plt

import config

class FFT(luigi.Task):
    """
    Data is expected to be in csv format.
    Data is assumed to be 1 measure per day.
    Subclass must implement requires() and output().

    Required Attributes
    ----------
    col_names : str []
        Column names of upstream file data.
        The date column should come first eg : ['date', 'my_values']
    """
    def run(self):
        for i, inp in enumerate(self.input()):
            print(" === " + inp.path + " === \n")
            dta = pandas.read_csv(inp.path,  header=0, quotechar='"')#, names=self.col_names)

            dcol = dta[self.col_names[1]]
            dfcol = dcol.apply(lambda x: float(str(x).split()[0].replace(',', ''))) #  rm commas in values

            # Number of samplepoints
            N = len(dfcol)
            # sample spacing
            T = 1.0 / 800.0
            x = np.linspace(0.0, N*T, N)
            y = dfcol
            yf = scipy.fftpack.fft(y)
            xf = np.linspace(0.0, 1.0/(2.0*T), N/2)

            plt.clf()

            # plot 0-inf
            # plt.plot(xf, 2.0/N * np.abs(yf[0:N/2]))

            # plot 1-inf
            plt.plot(xf[1:], 2.0/N * np.abs(yf[0:int(N/2)])[1:])

            # log-scale
            # plt.semilogy(xf, 2.0/N * np.abs(yf[0:int(N/2)]))

            plt.savefig(self.output()[i].path)

            # with open(self.output()[i].path, 'w') as outfile:
            #     outfile.write("TODO: add results here")
