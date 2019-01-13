new organization & workflow to use catalyst.

# current workflow
```bash
cd cf2
python ./trade_algorithm.py
```

# old notes
```bash
source ./virtualEnv/bin/activate

catalyst ingest-exchange -x binance -f daily -i eth_btc

catalyst run -f cf2/trade_algorithm.py -x bitfinex --start 2017-1-1 --end 2017-11-30 -c usd --capital-base 1000 -o buy_btc_simple_out.pickle
```
