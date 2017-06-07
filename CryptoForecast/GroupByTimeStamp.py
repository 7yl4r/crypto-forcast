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
            count = 0
            weighted_sum = 0
            volume_sum = 0
            last_stamp = -1
            for line in fin:
                timestamp, price, volume = [x.strip() for x in line.split(',')]
                timestamp = int(timestamp)
                price = float(price)
                volume = float(volume)
                if last_stamp < 0:  # set first timeStamp
                    assert count == 0
                    last_stamp = timestamp

                if timestamp > last_stamp:
                    if volume_sum != 0:
                        average = weighted_sum/volume_sum
                        fout.write("{},{},{}\n".format(timestamp, average, volume_sum))
                        # print(timestamp,':',average)
                    # else:
                        # print("!")
                    # reset values
                    last_stamp = timestamp
                    count = 0
                    weighted_sum = 0
                    volume_sum = 0
                else:
                    # print("-")
                    weighted_sum += price * volume
                    volume_sum += volume
                    count += 1
