The idea here is pretty simple:

1. ingest time-series data
2. create forecast classifier(s)
3. predict on current data
4. profit!

# Implementation plan:
1. pick a primary model
2. reproduce model results on test set
3. attempt to model on (manually curated) new data
4. implement ingestion script once model fits reasonably well

# Ideas
## ingest
Hmm... what data to ingest... How about:
1. historical self-values (eg autoregression)
    1. http://api.bitcoincharts.com/v1/csv/
    2. more suggestions on [this SO answer](https://stackoverflow.com/questions/16143266/get-bitcoin-historical-data)
2. historical values of other crypto-currencies (CCF might be useful here if one lags the other)
3. [google trends data](https://trends.google.com/trends/explore?q=bitcoin,litecoin,ethereum) using
    1. [pytrends](https://github.com/GeneralMills/pytrends)
    2. [unofficial trends api](https://github.com/suryasev/unofficial-google-trends-api)
    3. [trends csv downloader](https://github.com/pedrofaustino/google-trends-csv-downloader)
4. social media? news? idk.
5. other markets historical data?

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
3. good ol' fashioned autoregressors
    1. my old [behavAR](https://github.com/7yl4r/BehavAR) project
        1. also see [this script](https://github.com/PIELab/interventionViz/blob/master/behavARX.py)
4. frequency analysis
