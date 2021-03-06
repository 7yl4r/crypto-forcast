import scipy.stats as st


class FlexyIndicator(object):
    """
    Base Indicator with slightly flexible settings.
    This combines a preset strategy with a tiny bit of on-line adaptation.
    """

    def __init__(
        self,
        fn, fn_kwargs={},
        a_p_std=0.3413, a_p_mean=0,
    ):
        """
        Assumes normal distribution.
        Initial (a priori (a_p)) values used until enough observational
        data has been collected.

        Keeps track of distribution of values & adjusts strategy if value is
            non-normal around 0 mean.

        params:
        -------
        a_p_std: float
            a priori standard deviation
        a_p_mean: float
            a priori mean
        """
        self.fn = fn
        self.fn_kwargs = fn_kwargs
        self.mean = a_p_mean
        self.std = a_p_std
        # TODO: set function

    def get_value(self, context, data):
        # TODO: Update mean & std using incoming data?
        #       Kind of re-creating a Kalman filter here.
        #       Maybe we should just use that.
        return self.normalize_value(
            self.fn(context, data, **self.fn_kwargs)
        )

    def normalize_value(self, value):
        """
        Normalizes value to [-1, 1] using std & mean.
        +1 == mean + std*4
        -1 == mean - std*4
        """
        std_score = (value - self.mean) / self.std
        # return std_score/(4)  # rough linear approx
        return 2.0*st.norm.cdf(std_score)-1.0
        # TODO: cut off out of bounds [-1, 1]

    def invert_value(self, value):
        """
        Get value on opposite side of gaussian curve by
        flipping value across the average.
        """
        return self.mean - (value - self.mean)
