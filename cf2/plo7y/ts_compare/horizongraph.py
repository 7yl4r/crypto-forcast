"""
Creates a Horizon graph according to Panopticon.
See https://idl.cs.washington.edu/papers/horizon/ for further explaination.

Example usage:
```
from horizongraph import Horizon

plot = Horizon().run(x,y,labels, bands=3)
plot.subplots_adjust(left=0.07, right=0.998, top=0.99,bottom=0.01)
pp = PdfPages('multipage.pdf')
plot.savefig(pp, format="pdf")
pp.close()
```

Based on https://github.com/thomaskern/horizongraph_matplotlib
"""

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy


class InputError(Exception):
    def __init__(self, value):
        self.value = value


class Horizon(object):

    # public methods

    def run(
        self, x, y, labels, figsize=(20, 3), bands=3,
        colors=(
            # dark blue, med blue, light blue, dark red, med red, light red
            "#8BBCD4", "#2B7ABD", "#0050A0", "#EF9483", "#E02421", "#A90E0A"
        )
    ):
        """Return the entire graph and its plt object

        Look at DataTransformer.transform to see how the data is transformed.

        Keyword arguments:
        ------------------
        x: single array with x values.
            Distance between neighboring entries have to be the same
        y: two-dimansional array with y values for each entry.
        labels: array with strings, shown as the labels on the y-axis.
        figsize: (a,b)
            used when creating the figure (optional)
        bands:
            default is 3
        colors: array with the colors used for the bands.
            from dark to light blue, then from dark red to light red.

        Requirements:
        -------------
        len(y[i]) == len(x) for all 0 <= i < len(y)
        len(y[0]) == len(labels)
        len(colors) == 2*bands

        RETURN:
        -------
        plt object
        """
        self.check_valid_params(x, y, labels, figsize, bands, colors)
        n = len(y)

        F = self.create_figure(figsize)
        self.data_munger = TimeZeroCenteredDataTransformer(y, bands)

        for i in range(n):
            ax = F.add_subplot(n, 1, i+1)
            transformed_x, bands = self.data_munger.transform(y[i], x)

            for idx, band in enumerate(bands):
                ax.fill_between(transformed_x[idx], 0, band, color=colors[idx])

            self.adjust_visuals_line(x, y[i], self.data_munger, ax, i, labels)

        return plt

    # private methods
    def create_figure(self, figsize):
        F = plt.figure(figsize=figsize)
        F.clf()
        return F

    def set_theme(self, ax):
        """Hides all ticks and labels on both axes"""
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(False)

    def adjust_visuals_line(self, x, y, df, ax, i, labels):
        """Adjusts the subplot: height, width, labels"""
        plt.xlim(0, x[-1])
        plt.ylim(0, df.get_max()/3)
        self.set_theme(ax)
        ax.get_yaxis().set_visible(True)
        ax.set_yticks([])

        label = (
            '(+/-){:1.0E} {}\n    {:+1.0E}'
        ).format(
            self.data_munger.get_y_label_max(y),
            labels[i],
            self.data_munger.get_y_label_min(y),
        )
        font_p = FontProperties()
        font_p.set_family('monospace')
        ax.set_ylabel(
            label,
            ha='left', va='center', ma='left', rotation="horizontal",
            fontproperties=font_p
        )

    def check_valid_params(self, x, y, labels, figsize, bands, colors):
        """Checks parameters, throws an InputError if parameters are invalid"""
        if bands * 2 != len(colors):
            raise InputError("Number of bands invalid for number of colors")

        if len(y) != len(labels):
            raise InputError("Lengths of arrays y and labels are different")

        for i in y:
            if len(x) != len(i):
                raise InputError("Lengths of arrays x and y are different")


# ----------------------------------------------------------------------
# DATA TRANSFORMERS:
# ----------------------------------------------------------------------
class SharedAxisDataTransformer(object):
    """
    Transforms x & y data for horizongraphs all having shared x & y
    """

    def __init__(self, y, bands):
        """
        y: array of all y-values
        bands: number of bands
        """
        self.min = 0
        self.max = 0

        self.num_band = bands
        self.band = 0
        self.set_data(y)

    # public methods
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

    # private methods
    def set_data(self, data):
        """Instantiates all data-related properties.

        Keyword arguments:
        data: array of all y-values

        band: maximum number of y-values divided by the number of bands.
        max/min is set according to the values in data
        """
        self.max = max(max(data))
        self.min = min(min(data))

        if abs(self.max) > abs(self.min):
            self.min = self.max * -1

        if abs(self.max) < abs(self.min):
            self.max = self.min * -1

        self.band = self.max / self.num_band

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
