"""
"""

from unittest import TestCase
import pandas as pd
import io

from plo7y.testers.TSAnalyzer.TSAnalyzer import TSAnalyzer


class Test_is_evenly_spaced(TestCase):
    # tests:
    #########################
    def test_is_evenly_spaced_on_irregular_returns_false(self):
        """
        check if evenly spaced using example data from this s.o. q/a:
        https://stackoverflow.com/questions/25234941/python-regularise-irregular-time-series-with-linear-interpolation
        """
        data_str = io.StringIO('''\
            Values
            1992-08-27 07:46:48,28.0
            1992-08-27 08:00:48,28.2
            1992-08-27 08:33:48,28.4
            1992-08-27 08:43:48,28.8
            1992-08-27 08:48:48,29.0
            1992-08-27 08:51:48,29.2
            1992-08-27 08:53:48,29.6
            1992-08-27 08:56:48,29.8
            1992-08-27 09:03:48,30.0
        ''')
        data = pd.read_csv(data_str, squeeze=True)
        data.index = pd.to_datetime(data.index)

        self.assertFalse(
            TSAnalyzer(data).is_evenly_spaced
        )

    def test_is_evenly_spaced_on_regular_returns_true(self):
        """
        check if evenly spaced using example data from this s.o. q/a:
        https://stackoverflow.com/questions/25234941/python-regularise-irregular-time-series-with-linear-interpolation
        """
        df = pd.DataFrame(
            1,
            index=pd.date_range(
                '20130101 9:01',
                freq='h',
                periods=1000
            ),
            columns=['A']
        )

        self.assertTrue(
            TSAnalyzer(df).is_evenly_spaced
        )
