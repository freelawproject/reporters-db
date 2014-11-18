from reporters_db import REPORTERS, VARIATIONS_ONLY, EDITIONS
from unittest import TestCase
import datetime


class ConstantsTest(TestCase):
    def test_any_keys_missing_editions(self):
        """Have we added any new reporters that lack a matching edition?"""
        for r_name, r_items in REPORTERS.items():
            # For each reporter
            for item in r_items:
                # and each book in each reporter
                self.assertIn(
                    r_name, item['editions'],
                    msg="Could not find edition for key: %s" % r_name
                )

    def test_for_variations_mapping_to_bad_keys(self):
        """Do we have a variation that maps to a key that doesn't exist in the
        first place?
        """
        for variations in VARIATIONS_ONLY.values():
            for variation in variations:
                self.assertIn(
                    EDITIONS[variation], REPORTERS.keys(),
                    msg="Could not map variation to a valid reporter: %s" %
                        variation
                )

    def test_that_dates_are_converted_to_dates_not_strings(self):
        """Do we properly make the ISO-8601 date strings into Python dates?"""
        # Just test one.
        self.assertTrue(
            isinstance(REPORTERS['A.'][0]['editions']['A.']['start'],
                    datetime.datetime),
            msg="Dates in the reporters appear to be coming through as " \
                "strings."
        )
