This plot attempts to visualize multivariate optimization data.
The data is assumed to be a multi-dimensional dataframe with (somewhat) regular samples across the optimization space.
E.g.:

```csv
    var1,var2,var3,score
    0.11,2.02,3.33,69.69
```

The given `score` column represents how well this set of variables performed.
Methods here will generally assume that better (higher) scoring "areas" are more interesting than lower scoring areas.
