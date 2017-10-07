"""
performs seasonal decomposition for
    * week,
    * month( calendar: 30.44D & lunar: 29.53D),
    * quarter
    * year
season lengths. Outputs plots of original/trend/seasonality/residuals for each
as well as (TODO) ?some? metric of how well each season-len performs as a predictor.
"""

import luigi
import pandas
import matplotlib.pyplot as plt

import config
from plotters.seasonalDecompose import seasonalDecompose

class SeasonalAnalysis(luigi.Task):
    """
    Data is expected to be in csv format.
    Data is assumed to be 1 measure per day.

    Required Attributes
    ----------
    col_names : str []
        Column names of upstream file data.
        The date column should come first eg : ['date', 'my_values']
    """
    # Optional Attributes
    # ----------
    seasons=[7, 29.53, 30.44, 30.44*3, 365]
    #   season lengths to try out
    min_seasons=5
    #   dataset must contain this number of seasons else it will be excluded
    def run(self):
        dta = pandas.read_csv(self.input()[0].path, names=self.col_names, header=0)

        for season in self.seasons:
            if season*self.min_seasons < len(dta):
                seasonalDecompose(
                    dta[self.col_names[1]].astype('float64'),
                    saveFigName=self.output().path+".png",
                    dataResolution=1,
                    seasonLen=season
                )
            else :
                print("\n\nWARN: not enough seasons in data " +
                    "for season of len " + str(season) +
                    " min_seasons is " + str(self.min_seasons)
                )

        with open(self.output().path, 'w') as outfile:
            outfile.write("TODO: add results here")
