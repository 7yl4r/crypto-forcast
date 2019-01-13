import pandas as pd
perf = pd.read_pickle('buy_btc_simple_out.pickle')  # read in perf DataFrame
print(perf.head())
