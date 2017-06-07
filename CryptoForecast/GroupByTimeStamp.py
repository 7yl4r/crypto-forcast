"""
samples with timestamps close enough get summarized
"""

import luigi

import config
from DecompressPrices import DecompressPrices

class GroupByTimeStamp(luigi.Task):

    def requires(self):
        return [DecompressPrices()]

    def output(self):
        return luigi.LocalTarget(config.data_dir+"coinbaseUSD_grouped.csv")

    def run(self):
        with self.input()[0].open() as fin, self.output().open('w') as fout:
            # assumes timestamps are sorted
            # computes weighted average using volume & timestamps
            lastStamp = -1
            count = 0
            weighted_sum = 0
            volume_sum = 0
            lastStamp = 0
            for line in fin:
                timestamp, price, volume = [x.strip() for x in line.split(',')]
                timestamp = int(timestamp)
                price = float(price)
                volume = float(volume)
                if timestamp > lastStamp and lastStamp > 0:  # skip 1st one
                    average = weighted_sum/volume_sum
                    fout.write("{}:{}\n".format(timestamp, average))
                    # reset values
                    lastStamp = timestamp
                    count = 0
                    weighted_sum = 0
                    volume_sum = 0
                    lastStamp = 0
                else:
                    weighted_sum += price * volume
                    volume_sum += volume
                    count += 1
