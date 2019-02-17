class FlexyIndicator(object):
    """
    Base Indicator with slightly flexible settings.
    This combines a preset strategy with a tiny bit of on-line adaptation.
    """
    def __init__(
        self,
        fn,
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
        self.mean = a_p_mean
        self.std = a_p_std
        # TODO: set function

    def get_value(self):
        return self.fn()
