# ----------------------------------------------------------------------
# DATA TRANSFORMERS:
# ----------------------------------------------------------------------
import numpy


class SharedAxisDataTransformer(object):
    """
    Transforms x & y data for horizongraphs all having shared x & y.
    """

    def __init__(self):
        """
        y: array of all y-values
        bands: number of bands
        """
        self.min = 0
        self.max = 0

        self.band = 0
        self.data = []

    # === public methods

    def set_bands(self, bands):
        self.num_band = bands

    def get_max(self):
        """Returns the maximum y-value"""
        return self.max

    def get_y_label_min(self, y):
        """Return min value on  y axis"""
        # TODO: is this correct?
        return 0

    def get_y_label_max(self, y):
        """Return max value on y axis"""
        return self.get_max()

    def transform(self, y, x):
        """Transforms y-data into an array of bands

        IMPORTANT:
        Due to even distribution of the values of the bands, the highest
        absolute number of either the minimum or the maximum value is chosen.
        If self.min is larger than self.max, self.max is set to self.min.
        Otherwise the procedure is vice versa.
        Example:
        Given: self.min = -183; self.max = 134
        Reset: self.min = -183; self.max = 183

        Keyword arguments:
        Requires the two parameters to satisfy len(y) == len(x).

        RETURNS:
        --------
        array of new x positions
        array of bands for y values
            y values array has the length of NUM_BAND*2.
            All positive values are stored in the first NUM_BAND entries
            followed by the negative ones.
            The order for the positive/negative values is: dark, medium, light.

        """
        ret = []
        x1 = []
        one_step = x[1] - x[0]

        for i in range(self.num_band*2):
            b = []
            x_new = []

            for idx, y1 in enumerate(y):
                z = 0
                has_crossover = False

                if self.is_still_positive(i):
                    if y1 > 0:
                        z = self.calculate_new_y_value(i, y1)
                        self.crossover_beginning(
                            idx, x, one_step, b, x_new, y, self.smaller
                        )
                        has_crossover, new_x_value = self.crossover_ending(
                            idx, x, one_step, y, self.smaller
                        )
                else:
                    if y1 < 0:
                        z = self.calculate_new_y_value(i, abs(y1))
                        self.crossover_beginning(
                            idx, x, one_step, b, x_new, y, self.larger
                        )
                        has_crossover, new_x_value = self.crossover_ending(
                            idx, x, one_step, y, self.larger
                        )

                b.append(z)
                x_new.append(x[idx])
                if has_crossover:
                    x_new.append(new_x_value)
                    b.append(0)

            ret.append(b)
            x1.append(x_new)

        return x1, ret

    def add_series(self, series):
        """Instantiates all data-related properties.

        Keyword arguments:
        data: array of all y-values

        band: maximum number of y-values divided by the number of bands.
        max/min is set according to the values in data
        """
        self.data.append(series)
        data = self.data
        self.max = max(max(data))
        self.min = min(min(data))

        if abs(self.max) > abs(self.min):
            self.min = self.max * -1

        if abs(self.max) < abs(self.min):
            self.max = self.min * -1

        self.band = self.max / self.num_band

    # === private methods
    def transform_number(self, y1, top, bottom):
        """Calculates the new y-value for a specific value and band
        If y1 is larger than top, the maximum band value is returned.
        Else if y1 is between the band, the remaining value is returned.
        Else 0 is returned.
        """
        z = 0
        if bottom < y1 and y1 <= top:
            z = y1 - bottom
        elif y1 >= top:
            z = self.band
        return(z)

    def crossover_ending(self, idx, x, one_step, y, m):
        if len(y) > idx + 1 and m(y[idx+1], 0):
            return True, x[idx] + one_step/2.0
        else:
            return False, 0

    def larger(self, a, b):
        return a > b

    def smaller(self, a, b):
        return a < b

    def crossover_beginning(self, idx, x, one_step, b, x_new, y, m):
        """Appends 0 inbetween the current and next x-value IFF there is a
        crossover between positive and negative values
        """
        if idx > 0 and m(y[idx - 1], 0):
            x_new.append(x[idx] - one_step/2.0)
            b.append(0)

    def is_still_positive(self, i):
        """Returns true if the current index i is still within the number of
        bands
        """
        return i < self.num_band

    def calculate_new_y_value(self, i, y1):
        """Returns new y-value for a specific band"""
        top = (i % self.num_band + 1) * self.band
        bottom = (i % self.num_band) * self.band

        return self.transform_number(y1, top, bottom)


class MeanCenteredDataTransformer(SharedAxisDataTransformer):
    """
    Transforms x & y data for horizongraphs each with their own x & y.
    Accomplishes this by normalizing all bands to range [0,1] and fixing
    the 0 point to the mean of the series.
    """

    def get_max(self):
        return 1.0  # * self.num_band ?

    def get_y_label_min(self, y):
        """Return min value on  y axis"""
        return numpy.mean(numpy.array(y))

    def get_y_label_max(self, y):
        """Return max value on y axis"""
        y_arry = numpy.array(y)
        mean = numpy.mean(y_arry)
        return max(mean - numpy.min(y_arry), numpy.max(y_arry) - mean)

    def get_zero_of(self, y_i):
        return numpy.mean(numpy.array(y_i))

    def transform(self, y_i, x):
        y_arry = numpy.array(y_i)
        y_0 = self.get_zero_of(y_i)
        nmin = numpy.min(y_arry)
        nmax = numpy.max(y_arry)
        max_deviation = max(y_0 - nmin, nmax - y_0)
        # print("--- [{:9.3f} {:9.3f}] ---".format(nmin, nmax))
        y_bands = []
        x1 = []
        # normalize to [-1, 1]
        if max_deviation < 0:
            # nothing interesting in this series
            return [[0] * len(y_i)] * self.num_band*2
        # implied else
        normalized_y = [(val - y_0) / max_deviation for val in y_i]
        # print("--- [{:9.3f} {:9.3f}]".format(
        #     min(normalized_y), max(normalized_y)
        # ))
        # linear band crossing points:
        crossovers = numpy.linspace(0.0, 1.0, self.num_band + 1)
        # (+) bands first
        for sign in [1.0, -1.0]:
            for i in range(len(crossovers)-1):
                band = [0]*len(normalized_y)
                count = 0
                lower_bound = crossovers[i]
                upper_bound = crossovers[i+1]
                for ib in range(len(band)):
                    y_n = normalized_y[ib] * sign
                    if lower_bound < y_n:
                        if y_n < upper_bound:
                            band[ib] = abs(y_n) - crossovers[i]
                            count += 1
                        else:
                            band[ib] = 1.0
                    # else:
                    #     print("{} !< {} !< {}".format(
                    #         lower_bound, y_n, upper_bound
                    #     ))
                    # else leave it 0
                # print('bnd {:+4.2f}<x<{:+4.2f}\t|\t{}'.format(
                #     lower_bound, upper_bound, count
                # ))
                y_bands.append(band)
                x1.append(x)
        # import pdb; pdb.set_trace()
        return x1, y_bands


class TimeZeroCenteredDataTransformer(MeanCenteredDataTransformer):
    def get_zero_of(self, y_i):
        return y_i[0]

    def get_y_label_min(self, y):
        return self.get_zero_of(y)

    def get_y_label_max(self, y):
        y_arry = numpy.array(y)
        mean = numpy.mean(y_arry)
        return max(mean - numpy.min(y_arry), numpy.max(y_arry) - mean)

# class ManualYDataTransformer(MeanCenteredDataTransformer):
#     def __init__(self, y_bounds, *args, **kwargs):
#         """
#         params:
#         -------
#         y_bounds: list of tuples
#             bounds for each Y
#         """
#         self.y_bounds = y_bounds
#         super(ManualYDataTransformer)
#
#     def get_zero_of(self, y_i):
#         return self.y_bounds[0]
#
#     def get_y_label_max(self, y):
