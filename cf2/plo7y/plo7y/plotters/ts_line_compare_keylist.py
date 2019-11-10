"""Compare several timeseries with dataframe keys given in a list"""


def ts_compare_keylist(dta, x_key, y_key_list, figsize):
    dta.plot(x=x_key, y=y_key_list[0])
    dta[y_key_list].plot(
        figsize=figsize
    )
