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

from plo7y.ts_compare.horizon_data_transformers \
    import TimeZeroCenteredDataTransformer


class InputError(Exception):
    def __init__(self, value):
        self.value = value


class Horizon(object):
    def __init__(self, data_transformers=[]):
        if data_transformers == []:
            data_transformers = [TimeZeroCenteredDataTransformer()]
        self.data_transformers = data_transformers

    # public methods
    def run(
        self, x, y, labels, figsize=(20, 3), bands=3,
        colors=(
            # dark blue, med blue, light blue, dark red, med red, light red
            "#8BBCD4", "#2B7ABD", "#0050A0", "#EF9483", "#E02421", "#A90E0A"
        ),
        data_trans_indexes=[]
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
        F = self.create_figure(figsize)

        n = len(y)
        if data_trans_indexes == []:
            data_trans_indexes = [0]*n
        elif len(data_trans_indexes) != len(y):
            raise AssertionError(
                "# data transformer indexes ({}) must == # series ({})".format(
                    len(data_trans_indexes), len(y)
                )
            )

        # set up the data transformers
        for i in range(n):
            data_munger = self.data_transformers[data_trans_indexes[i]]
            data_munger.set_bands(bands)
            data_munger.add_series(y[i])

        # transform the data into bands
        for i in range(n):
            data_munger = self.data_transformers[data_trans_indexes[i]]
            ax = F.add_subplot(n, 1, i+1)
            transformed_x, bands = data_munger.transform(y[i], x)

            for idx, band in enumerate(bands):
                ax.fill_between(transformed_x[idx], 0, band, color=colors[idx])

            self.adjust_visuals_line(x, y[i], data_munger, ax, i, labels)

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

    def adjust_visuals_line(self, x, y, data_munger, ax, i, labels):
        """Adjusts the subplot: height, width, labels"""
        plt.xlim(0, x[-1])
        plt.ylim(0, data_munger.get_max()/3)
        self.set_theme(ax)
        ax.get_yaxis().set_visible(True)
        ax.set_yticks([])

        label = (
            '(+/-){:1.0E} {}\n    {:+1.0E}'
        ).format(
            data_munger.get_y_label_max(y),
            labels[i],
            data_munger.get_y_label_min(y),
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
