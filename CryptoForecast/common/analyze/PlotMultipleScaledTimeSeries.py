"""
creates plot of multiple time-series loaded from csv with y-axis all scaled to
range {-100, 100}
"""

import luigi
import numpy as np
import pandas
import matplotlib.pyplot as plt
import datetime

class PlotMultipleScaledTimeSeries(luigi.Task):

    def get_index_transform(self, i ):
        """ returns function to transform index value before feeding to plotter """
        return lambda d: datetime.datetime.strptime(d, '%Y-%m-%d')

    def get_values(self, i ):
        """ returns function to fetch list of values out of dataframe """
        return lambda dta: [100.0/max(dta.max(), -dta.min()) * v for v in dta.iloc[:, 0]]

    def run(self):
        for i, inp in enumerate(self.input()):
            dta =  pandas.read_csv(inp.path, index_col=0)
            plt.plot(
                [self.get_index_transform(i)(d) for d in dta.index],
                self.get_values(i)(dta)
            )

        print("\nsaving plot to ", self.output().path, "...\n")
        plt.savefig(self.output().path, bbox_inches='tight')
