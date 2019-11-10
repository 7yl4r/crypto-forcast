import pandas
import seaborn


def ts_downsample_compare_two(
    dta, x_key, y_key, y_group_by_key, figsize
):
    dta.index = pandas.to_datetime(dta[x_key])
    # === downsample until we find a reasonable number of violins
    #    since I wasn't sure how to calculate the frequency of the
    #    existing dataset this brute-forces by starting at a huge
    #    resampling period & moving down until we get a good number
    #    of violins.
    PERIODS = [  # typical data frequency periods sorted descending
        '1200m', '120m', '60m', '24m', '12m', '6m',
        '120d', '90d', '30d', '14d', '7d', '1d',
    ]
    # ideal number of violins should be > LEN_MIN && < LEN_MAX
    LEN_MIN = 5
    LEN_MAX = 9
    assert len(dta) > LEN_MAX
    resample = []
    period_n = 0
    while len(resample) < LEN_MIN:
        new_period = PERIODS[period_n]
        print('resampling to frequency 1/{}...'.format(new_period))
        resample = dta.resample(new_period)
        # indexError here means we need to add smaller periods
        #     at the end of the list
        period_n += 1
    if len(resample) > LEN_MAX:
        raise AssertionError(
            "Oops, we went too far; "
            " more periods are needed between the last two."
        )
    else:
        print("success. Resampled into {} bins.".format(len(resample)))

    resample = resample.sum()[y_key]
    dta['x_resampled'] = [
        resample.index[resample.index.get_loc(
            pandas.to_datetime(v), method='nearest'
        )]
        for v in dta[x_key]
    ]

    print("counts in each group:")
    print(dta[y_group_by_key].value_counts())
    # TODO: assert these are evenly spread

    # === choose inner vizualization
    # NOTE: you may increase this max if you have a supercomputer
    MAX_LINES_PLOTTABLE = 10000
    if len(dta) < figsize[0]*200 and len(dta) < MAX_LINES_PLOTTABLE:
        inner_viz = "stick"
    else:
        inner_viz = "box"

    # choose amount of smoothing
    if len(dta) > 10000:
        bandwidth = 0.1
    elif len(dta) > 5000:
        bandwidth = 0.2
    elif len(dta) > 1000:
        bandwidth = 0.3
    else:
        bandwidth = 'scott'

    # do plot
    axes = seaborn.violinplot(
        x='x_resampled', y=y_key, hue=y_group_by_key, data=dta,
        scale="count",
        inner=inner_viz, bw=bandwidth,
        split=True, cut=0
    )
    axes.set_xticks([])  # remove ticks b/c they look bad
    axes.set_xlabel('{} / {}'.format(dta[x_key][0], dta[x_key][-1]))
