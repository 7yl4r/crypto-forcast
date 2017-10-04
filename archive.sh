#!/bin/bash
# moves current data into archive

dirname=archive/`date --iso-8601=minutes`
mkdir $dirname
mkdir $dirname/data
mv data/* $dirname/data/.
