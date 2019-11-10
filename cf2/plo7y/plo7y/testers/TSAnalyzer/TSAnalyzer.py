"""
Get detailed analysis of a timeseries.
"""
from functools import lru_cache


class TSAnalyzer():
    # TODO: trend & frequency analysis
    # TODO: normality of residuals
    # TODO: autocorrelation
    # pd.plotting.autocorrelation_plot(df[y_key])
    # TODO: is_stationary
    # TODO: differencing to make stationary
    # df[y_key].diff(periods=30).plot()

    # https://github.com/datascopeanalytics/traces

    def __init__(self, dataframe):
        self.df = dataframe

    @property
    @lru_cache()
    def is_evenly_spaced(self):
        """
        True if timedelta between each pair of points is the same.
        Assumes series is sorted & index is datetimes.
        """
        t_col = self.df.index
        expected_td = t_col[0] - t_col[1]
        for i in range(len(t_col)-1):  # for each pair of points
            if t_col[i] - t_col[i+1] != expected_td:
                return False
        else:
            return True

    @lru_cache()
    def grouped_dta(self, y_group_by_key, x_key, y_key):
        return self.df.groupby([y_group_by_key]).agg({
            y_group_by_key: 'first',
            x_key: 'first',
            y_key: sum,
        })[y_key]

    @lru_cache()
    def is_x_too_dense(self, x_key, y_key, y_group_by_key, figsize, dpi):
        x_dppi = len(self.df.groupby(x_key)) / figsize[0]

        if x_dppi > dpi/3:  # too dense
            return True
        else:
            return False
