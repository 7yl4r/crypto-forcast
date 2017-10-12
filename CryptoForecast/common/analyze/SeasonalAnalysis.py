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
import math

import config
from plotters.seasonalDecompose import seasonalDecompose, plotImage

class SeasonalAnalysis(luigi.Task):
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
    # Optional Attributes
    # ----------
    seasons=None#[7, 29.53, 30.44, 30.44*3, 365]
    #   season lengths to try out
    #
    min_seasons=2
    #   dataset must contain this number of seasons else it will be excluded
    def run(self):
        for i, inp in enumerate(self.input()):
            print(" === " + inp.path + " === \n")
            dta = pandas.read_csv(inp.path,  header=0, quotechar='"')#, names=self.col_names)
            
            if self.seasons is None:
                self.seasons = range(2, math.ceil(len(dta)/self.min_seasons+2))

            seasonal_arry = [[0]*len(dta)]*(max(self.seasons)+1)
            trend_arry    = [[0]*len(dta)]*(max(self.seasons)+1)
            resid_arry    = [[0]*len(dta)]*(max(self.seasons)+1)
            for season in self.seasons:
                if season*self.min_seasons < len(dta):
                    dcol = dta[self.col_names[1]]
                    dfcol = dcol.apply(lambda x: float(str(x).split()[0].replace(',', ''))) #  rm commas in values

                    trend, seasonal, residuals = seasonalDecompose(
                        dfcol.astype('float64'),
                        saveFigName=self.output()[i].path+".png",
                        dataResolution=1,
                        seasonLen=season
                    )
                    seasonal_arry[round(season)] = [0 if math.isnan(x) else x for x in seasonal]
                    trend_arry[round(season)]    = [0 if math.isnan(x) else x for x in trend]
                    resid_arry[round(season)]    = [0 if math.isnan(x) else x for x in residuals]
                else :
                    print("\n\nWARN: not enough seasons in data " +
                        "for season of len " + str(season) +
                        " min_seasons is " + str(self.min_seasons)
                    )
            plotImage(seasonal_arry, self.output()[i].path+"_arry_seasonal.png")
            plotImage(trend_arry   , self.output()[i].path+"_arry_trend.png")
            plotImage(resid_arry   , self.output()[i].path+"_arry_residual.png")

            with open(self.output()[i].path, 'w') as outfile:
                outfile.write("TODO: add results here")
