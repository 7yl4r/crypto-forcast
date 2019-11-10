"""
NOTE: many of these tests only test that the plotting methods
    are able to finish without throwing an exception.
    TODO: Should we be checking the output figures somehow?
"""

import sys
from unittest import TestCase

from plo7y.reporters.ts_compare import ts_compare


class Test_ts_compare(TestCase):
    # tests:
    #########################
    def test_obis_occurrence(self):
        """ test ts compare on obis occurence data """
        ts_compare(
            "test_data/obis.csv",
            x_key="eventDate",
            y_key_list=["X", "year"],
            savefig="/tmp/plo7y_test_{}.png".format(
                sys._getframe().f_code.co_name
            ),
        )

    def test_obis_group_by_species_on_X(self):
        """ test ts compare on obis occurence data using y_group_by_key"""
        ts_compare(
            "test_data/obis.csv",
            x_key="eventDate",
            y_key="X",
            y_group_by_key="species",
            savefig="/tmp/plo7y_test_{}.png".format(
                sys._getframe().f_code.co_name
            ),
        )

    def test_obis_group_by_species_on_occurrence_status(self):
        """ test ts compare on subset of obis occurence using y_group_by_key"""
        ts_compare(
            "test_data/occurrenceStatus.csv",
            x_key="eventDate",
            y_key="occurrenceStatus",
            y_group_by_key="species",
            savefig="/tmp/plo7y_test_{}.png".format(
                sys._getframe().f_code.co_name
            ),
        )

    def test_obis_occurrence_empty(self):
        """ test ts compare on 0-length obis occurence data"""
        with self.assertRaises(AssertionError):
            ts_compare(
                "test_data/obis_empty.csv",
                x_key="eventDate",
                y_key="X",
                y_group_by_key="species",
                savefig="/tmp/plo7y_test_{}.png".format(
                    sys._getframe().f_code.co_name
                ),
            )
