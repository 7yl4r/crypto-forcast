#!/bin/bash
# moves current data into archive

dirname=archive/`date --iso-8601=minutes`
mkdir $dirname
mkdir $dirname/data
mv data/* $dirname/data/.

# uhh... put ingested data back b/c I don't want to worry about making those
#   work right now.
mkdir data/ingest
mv $dirname/data/ingest/* data/ingest/.
