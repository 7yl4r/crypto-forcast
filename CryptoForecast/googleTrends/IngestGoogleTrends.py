"""
reads in data from google trends about bitcoin using [pytrends](https://github.com/GeneralMills/pytrends)
"""

import luigi

from pytrends.request import TrendReq

import config
from secrets import google_username, google_password

class IngestGoogleTrends(luigi.Task):

    def requires(self):
        return []

    def output(self):
        return luigi.LocalTarget(config.data_dir+"ingest/bitcoin_trends.csv")

    def run(self):
        path = ""

        # Login to Google. Only need to run this once, the rest of requests will use the same session.
        pytrend = TrendReq(google_username, google_password, custom_useragent='crypto-forecast ingest script')

        # Create payload and capture API tokens. Only needed for interest_over_time(), interest_by_region() & related_queries()
        pytrend.build_payload(kw_list=['bitcoin'])

        # Interest Over Time
        interest_over_time_df = pytrend.interest_over_time()

        # print(interest_over_time_df)
        print("\nsaving plot to ", self.output().path, "...\n")

        interest_over_time_df.to_csv(self.output().path)
