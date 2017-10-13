import os

import luigi

import config
from common.analyze.FFT import FFT
from kaggle.IngestKaggle import IngestKaggle

class KaggleFFT(FFT):

    def __init__(self):
        super().__init__()
        self.filenames = []
        for fname in os.listdir(config.data_dir+"ingest/kaggle/"):
            if fname.endswith(".csv"):
                self.filenames.append(fname)

    def requires(self):
        return IngestKaggle()

    def output(self):
        return [
            luigi.LocalTarget(
                config.data_dir+"/analyze/kaggle_{}_FFT.png".format(filename)
            ) for filename in self.filenames
        ]

    col_names=['Date','Close']
