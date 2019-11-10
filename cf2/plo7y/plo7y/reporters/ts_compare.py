"""
Compare a set of N timeseries.

Examples:
---------
* stock prices
* portfolio values
* temperatures in two locations
"""
import matplotlib.pyplot as plt

from plo7y._internal.get_dataframe import get_dataframe
from plo7y.recommenders.ts_compare import recommend


def x_too_dense(dta, x_key, y_key, y_group_by_key, figsize, dpi):
    x_dppi = len(dta.groupby(x_key)) / figsize[0]

    if x_dppi > dpi/3:  # too dense
        return True
    else:
        return False


def ts_compare(
    dta,
    figsize=(10, 7.5),  # width, height in inches (default 100 dpi)
    dpi=100,
    legend=True,
    savefig=None,
    **kwargs
):
    """
    Parameters
    ----------
    dta : pandas.DataFrame
        dataframe containing all columns
    x_key : str
        x-axis column name
    y_key : str
        y-axis column name
    y_key_list : str[]
        y-axis column names (for multiple y_key)
    y_group_by_key : str
        a single column with catagorical values used which
        will be grouped to add multiple series to the y-axis
    savefig : str
        filepath to save output, else show
    """
    dta = get_dataframe(dta)
    if kwargs.get("method") is None:
        method = recommend(
            dta,
            dpi=dpi,
            figsize=figsize,
            legend=legend,
            **kwargs
        )

    # timeseries rows must be in order
    dta.sort_values(kwargs.get("x_key"), inplace=True)

    # === drop missing values:
    orig_len = len(dta)
    if kwargs.get("y_key_list") is not None:
        col_list = kwargs.get("y_key_list") + [kwargs.get("x_key")]
    elif kwargs.get("y_group_by_key") is not None:
        col_list = [
            kwargs.get("y_group_by_key"),
            kwargs.get("x_key"),
            kwargs.get("y_key")
        ]
    else:
        raise ValueError(
            "Must pass multiple y-cols or give group-by col."
        )
    dta.dropna(subset=col_list, inplace=True)
    print("{} NA values-containing rows dropped; {} remaining.".format(
        orig_len - len(dta), len(dta)
    ))
    if len(dta) < 2:
        raise ValueError("Too few valid rows to create plot.")

    # do the plotting
    print('plotting w/ method "{}"'.format(method))
    method(dta=dta)

    if kwargs.get("title") is not None:
        plt.title(kwargs.get("title"))
    if kwargs.get("ylabel") is not None:
        plt.ylabel(kwargs.get("ylabel"))

    if savefig is not None:
        plt.savefig(savefig, bbox_inches='tight')
        plt.clf()
    else:
        plt.show()
