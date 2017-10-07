#!/bin/bash
# moves current data into archive

dirname=archive/`date --iso-8601=minutes`
mkdir $dirname
mkdir $dirname/data
mv data/* $dirname/data/.

# create data directory structure
mkdir data/ingest
mkdir data/preprocess
mkdir data/analyze
mkdir data/model
mkdir data/model-evaluation
mkdir data/forecast
mkdir data/action
mkdir data/action-evaluation

# uhh... put ingested data back b/c I don't want to worry about
#   making those work right now...
mv $dirname/data/ingest/* data/ingest/.
# aaaand also this pre-processing that isn't working...
mv $dirname/data/preprocess/coinbaseUSD.csv data/preprocess/coinbaseUSD.csv
