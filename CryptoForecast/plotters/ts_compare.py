"""
Compare a set of N timeseries.

Examples:
---------
* stock prices
* portfolio values
* temperatures in two locations

TODO: use horizonplots for large N?

"""
import matplotlib.pyplot as plt


def ts_compare(
    dta,
    *args,
    x_key=None,
    y_key=None,
    y_key_list=None,
    # TODO: some of these args are generalizable...
    #       how best to share them between functions?
    savefig=None,
    title=None,
    ylabel=None,
    figsize=(12, 8),
    legend=True,
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
    savefig : str
        filepath to save output, else show
    """
    assert y_key is None or y_key_list is None
    assert y_key_list is None or len(y_key_list) > 0
    if y_key_list is not None:
        dta.plot(x=x_key, y=y_key_list[0])
        dta[y_key_list].plot(
            figsize=figsize
        )
    elif y_key is not None:
        dta.plot(x=x_key, y=y_key)
    else:  # both None
        dta.plot(x=x_key, legend=legend)

    if title is not None:
        plt.title(title)
    if ylabel is not None:
        plt.ylabel(ylabel)

    if savefig is not None:
        plt.savefig(savefig, bbox_inches='tight')
    else:
        plt.show()
