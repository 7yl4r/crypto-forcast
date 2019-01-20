"""
Creates a Horizon graph according to Panopticon (http://www.panopticon.com/).

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

class InputError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return rep(self.value)

class Horizon:

  # public methods

  def run(self, x, y, labels, figsize=(20,3), bands=3, colors=("#8BBCD4","#2B7ABD","#0050A0","#EF9483","#E02421", "#A90E0A")): # dark blue, medium blue, light blue, dark red, medium red, light red
    """ Return the entire graph and its plt object

        Look at DataTransformer.transform to see how the data is transformed.

        Keyword arguments:
        x: single array with x values. Distance between neighboring entries have to be the same
        y: two-dimansional array with y values for each entry.
        labels: array with strings, shown as the labels on the y-axis.
        figsize: (a,b) used when creating the figure (optional)
        bands: default is 3
        colors: array with the colors used for the bands. from dark to light blue, then from dark red to light red.

        Requirements:
        len(y[i]) == len(x) for all 0 <= i < len(y)
        len(y[0]) == len(labels)
        len(colors) == 2*bands

        RETURN: plt object
    """

    self.check_valid_params(x,y,labels,figsize,bands,colors)
    n = len(y)

    F = self.create_figure(figsize)
    df = DataTransformer(y, bands)

    for i in range(n):
      ax = F.add_subplot(n, 1, i+1)
      transformed_x, bands = df.transform(y[i], x)

      for idx,band in enumerate(bands):
        ax.fill_between(transformed_x[idx],0,band,color=colors[idx])

      self.adjust_visuals_line(x, df, ax, i, labels)

    return plt

  # private methods
  def create_figure(self, figsize):
    F = plt.figure(figsize=figsize)
    F.clf()
    return F

  def set_theme(self,ax):
    """ hides all ticks and labels on both axes """
    ax.get_yaxis().set_visible(False)
    ax.get_xaxis().set_visible(False)

  def adjust_visuals_line(self, x, df, ax, i, labels):
    """ adjusts the subplot: height, width, labels """
    plt.xlim(0,x[-1])
    plt.ylim(0,df.get_max()/3)
    self.set_theme(ax)
    ax.get_yaxis().set_visible(True)
    ax.set_yticks([])
    ax.set_ylabel(labels[i], rotation="horizontal")

  def check_valid_params(self, x,y,labels, figsize, bands, colors):
    """ checks parameters, throws an InputError if parameters are invalid """

    if bands * 2 != len(colors):
      raise InputError("Number of bands invalid for number of colors")

    if len(y) != len(labels):
      raise InputError("Lengths of arrays y and labels are different")

    for i in y:
      if len(x) != len(i):
        raise InputError("Lengths of arrays x and y are different")

# ----------------------------------------------------------------------
# DATA TRANSFORMER:
# ----------------------------------------------------------------------
class DataTransformer:

  def __init__(self, y, bands):
    """ y: array of all y-values
    bands: number of bands
    """
    self.min = 0
    self.max = 0

    self.num_band = bands
    self.band = 0
    self.set_data(y)

  # public methods
  def get_max(self):
    """ Returns the maximum y-value """
    return self.max

  def transform(self, y, x):
    """ Transforms y-data into an array of bands

    IMPORTANT:
    Due to even distribution of the values of the bands, the highest absolute number of either the minimum or the maximum value is chosen. If self.min is larger than self.max, self.max is set to self.min. Otherwise the procedure is vice versa.
    Example:
    Given: self.min = -183; self.max = 134
    Reset: self.min = -183; self.max = 183

    Keyword arguments:
    Requires the two parameters to satisfy len(y) == len(x).

    RETURN: (array of new x positions, array of bands for y values).
    y values array has the length of NUM_BAND*2.
    All positive values are stored in the first NUM_BAND entries followed by the negative ones.
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
            self.crossover_beginning(idx, x, one_step, b, x_new, y, self.smaller)
            has_crossover, new_x_value = self.crossover_ending(idx, x, one_step,y, self.smaller)
        else:
          if y1 < 0:
            z = self.calculate_new_y_value(i, abs(y1))
            self.crossover_beginning(idx, x, one_step, b, x_new, y, self.larger)
            has_crossover, new_x_value = self.crossover_ending(idx, x, one_step,y, self.larger)

        b.append(z)
        x_new.append(x[idx])
        if has_crossover:
          x_new.append(new_x_value)
          b.append(0)

      ret.append(b)
      x1.append(x_new)

    return x1,ret

  # private methods
  def set_data(self, data):
    """ Instantiates all data-related properties.

    Keyword arguments:
    data: array of all y-values

    band: maximum number of y-values divided by the number of bands.
    max/min is set according to the values in data  """

    self.max = max(max(data))
    self.min = min(min(data))

    if abs(self.max ) > abs(self.min):
      self.min = self.max * -1

    if abs(self.max ) < abs(self.min):
      self.max= self.min * -1

    self.band = self.max / self.num_band

  def transform_number(self,y1, top, bottom):
    """ Calculates the new y-value for a specific value and band
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
        return True,x[idx] + one_step/2.0
    else:
      return False, 0

  def larger(self, a, b):
    return a > b

  def smaller(self, a, b):
    return a < b

  def crossover_beginning(self, idx, x, one_step, b, x_new,y, m):
    """ Appends 0 inbetween the current and next x-value IFF there is a crossover between positive and negative values """
    if idx > 0 and m(y[idx - 1], 0):
       x_new.append(x[idx] - one_step/2.0)
       b.append(0)

  def is_still_positive(self,i):
    """ Returns true if the current index i is still within the number of bands """
    return i < self.num_band

  def calculate_new_y_value(self,i,y1):
    """ Returns new y-value for a specific band """
    top = (i % self.num_band + 1) * self.band
    bottom = (i % self.num_band) * self.band

    return self.transform_number(y1, top , bottom)
