The idea here is pretty simple:

1. ingest time-series data
2. create forecast classifier(s)
3. predict on current data
4. profit!

# Usage:
```bash
source ./virtualEnv/bin/activate
`luigid`  # to start the scheduler
`python CryptoForecast/run_luigi.py MyTaskName`
```

# Implementation plan:
1. pick a primary model
2. reproduce model results on test set
3. attempt to model on (manually curated) new data
4. implement ingestion script once model fits reasonably well

# Ideas
*legend*
* :hourglass: in-progress
* :white_check_mark: done
* :no_entry_sign: fail

## ingest
Hmm... what data to ingest... How about:
1. :hourglass: historical self-values (eg autoregression)
    1. http://api.bitcoincharts.com/v1/csv/
    2. more suggestions on [this SO answer](https://stackoverflow.com/questions/16143266/get-bitcoin-historical-data)
2. :hourglass: historical values of other crypto-currencies (CCF might be useful here if one lags the other)
3. :hourglass: [google trends data](https://trends.google.com/trends/explore?q=bitcoin,litecoin,ethereum) using
    1. [pytrends](https://github.com/GeneralMills/pytrends)
    2. [unofficial trends api](https://github.com/suryasev/unofficial-google-trends-api)
    3. [trends csv downloader](https://github.com/pedrofaustino/google-trends-csv-downloader)
4. sentiment analysis
    1. [twitter ingest](https://stackoverflow.com/questions/21579999/count-number-of-results-for-a-particular-word-on-twitter-api-v1-1) (NLP sold separately)
    2. stack overflow metrics ( ethereum / monero communities or question volumes on s.o. itself ) 

### Exogenous Evaluation Methods
1. granger causality test (and similar)
    1. [statsmodels grangercausalitytests](http://www.statsmodels.org/dev/generated/statsmodels.tsa.stattools.grangercausalitytests.html)
    2. [pretty causality matrix from nitime](http://nipy.org/nitime/examples/granger_fmri.html)
    3. [granger causality on non-stationary data](http://davegiles.blogspot.no/2011/04/testing-for-granger-causality.html)
    4. [other causality predictor(s) from kaggle cause-effect-pairs](https://www.kaggle.com/c/cause-effect-pairs/discussion/5702)
    5. [MVGC method)](http://erramuzpe.github.io/C-PAC/blog/2015/06/10/multivariate-granger-causality-in-python-for-fmri-timeseries-analysis/)
2. :hourglass: cross-correlation function
    
## pre-processing
1. USD values could be adjusted using [CPI values](http://www.usinflationcalculator.com/inflation/consumer-price-index-and-annual-percent-changes-from-1913-to-2008/) from [bls.gov data](https://download.bls.gov/pub/time.series/cu/)

## Analysis
1. :white_check_mark: frequency analysis
    1. :white_check_mark: FFT
    2. :white_check_mark: seasonal decomposition
    3. :hourglass: ACF & PACF


## Modeling
Time series models... For these I like:
1. Long short-term memory NN (LSTM NN) built on
    1. keras:
        1. [jaungier's](https://github.com/jaungiers/LSTM-Neural-Network-for-Time-Series-Prediction)
        2. [+ recurrent](https://github.com/yxg383/Time-Series-Prediction-with-LSTM-Recurrent-Neural-Networks-in-Python-with-Keras)
        3. [another w/ recurrent](https://github.com/Yifeng-He/Deep-Learning-Time-Series-Prediction-using-LSTM-Recurrent-Neural-Networks)
        4. [+ sequential model](https://github.com/gcarq/keras-timeseries-prediction)
    2. theano:
        1. [jgpavez](https://github.com/jgpavez/LSTM---Stock-prediction)
        2.
    3. custom:
        1. [CasiaFan](https://github.com/CasiaFan/time_seires_prediction_using_lstm)
2. Fuzzy Time Series Predictions
    1. [asiviero](https://github.com/asiviero/fuzzy_time_series_predictor)
3. :hourglass: good ol' fashioned autoregressors
    1. :white_check_mark: my old [behavAR](https://github.com/7yl4r/BehavAR) project
        1. also see [this script](https://github.com/PIELab/interventionViz/blob/master/behavARX.py)
    2. :hourglass: ARIMA / ARIMAX
