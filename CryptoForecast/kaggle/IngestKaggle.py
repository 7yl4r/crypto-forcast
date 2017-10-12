""" wrapper class for manually ingested kaggle dataset files """

import os

import luigi

import config

class IngestKaggle(luigi.ExternalTask):
    def __init__(self):
        super().__init__()
        self.filenames = []
        for fname in os.listdir(config.data_dir+"ingest/kaggle"):
            if fname.endswith(".csv"):
                self.filenames.append(fname)

    def output(self):
        out = [
            luigi.LocalTarget(
                config.data_dir+"ingest/kaggle/{}".format(filename)
            ) for filename in self.filenames
        ]

        # print("\n\no:{}\n\n".format(out))
        return out
