Plotters in this directory explore the concept of plotting by "user goal" insead of by explicit request.
The plots should be named and organized with this in mind.

Good plotter names:
* ts_compare : compares 2+ time-series
* ts_histo   : histographic analysis on a single timeseries
* what_is_seasonality : fourier analysis to identify most likely seasonal periods
* how_much_seasonality : seasonal decomp
* ts_x_correlation_ness : how much x-correlation is there between two ts?

Bad plotter names:
* bar_plot
* stacked_area_plot
* violin_plot
* ccf

This is a rough concept; files are likely to get moved and renamed.
Addition of more "good plotter name" ideas and organization of the list above is encouraged.

These functions should be light(ish) wrappers around other plotting libraries, possibly providing choice of library backend and often guessing what the user might want.
