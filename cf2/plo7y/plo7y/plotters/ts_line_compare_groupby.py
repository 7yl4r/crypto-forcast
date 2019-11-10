"""Compare several pre-grouped timeseries using dataframe"""


def ts_compare_groupby(
    dta=None, *args, x_key, y_key, y_group_by_key, figsize, grouped_dta=None
):
    if grouped_dta is None:
        assert dta is not None
        grouped_dta = dta.groupby([y_group_by_key]).agg({
            y_group_by_key: 'first',
            x_key: 'first',
            y_key: sum,
        })[y_key]
    elif dta is not None:
        print(
            "NOTICE: pre-grouped data & ungrouped dataframe passed\n"
            "    dta not needed if grouped_dta is provided."
        )
    # else use grouped dta as passed in
    grouped_dta.plot(
        x=x_key, y=y_key, legend=True, figsize=figsize,
        kind='line',
    )
