import json
import os
import re
import datetime
from difflib import context_diff
from pathlib import Path
import six
from reporters_db import (
    REPORTERS,
    VARIATIONS_ONLY,
    EDITIONS,
    NAMES_TO_EDITIONS,
    REGEX_VARIABLES,
)
from unittest import TestCase

from reporters_db.utils import substitute_editions, recursive_substitute

VALID_CITE_TYPES = (
    "federal",
    "neutral",
    "scotus_early",
    "specialty",
    "specialty_west",
    "specialty_lexis",
    "state",
    "state_regional",
)


def emit_strings(obj):
    """Recursively get all the strings out of a JSON object.

    Convert ints to strs
    """
    if isinstance(obj, dict):
        # Feed the keys and items back into the function.
        for k, v in obj.items():
            for x in emit_strings(k):
                yield x
            for x in emit_strings(v):
                yield x
    elif isinstance(obj, list):
        for item in obj:
            for x in emit_strings(item):
                yield x
    elif isinstance(obj, int):
        yield str(int)
    elif isinstance(obj, six.text_type):
        yield obj


def iter_reporters():
    for reporter_abbv, reporter_list in REPORTERS.items():
        for reporter_data in reporter_list:
            yield reporter_abbv, reporter_list, reporter_data


def iter_editions():
    for reporter_abbv, reporter_list, reporter_data in iter_reporters():
        for edition_abbv, edition in reporter_data["editions"].items():
            yield edition_abbv, edition


class ConstantsTest(TestCase):
    def test_any_keys_missing_editions(self):
        """Have we added any new reporters that lack a matching edition?"""
        for reporter_abbv, reporter_list, reporter_data in iter_reporters():
            self.assertIn(
                reporter_abbv,
                reporter_data["editions"],
                msg="Could not find edition for key: %s" % reporter_abbv,
            )

    def test_for_variations_mapping_to_bad_keys(self):
        """Do we have a variation that maps to a key that doesn't exist in the
        first place?
        """
        for variations in VARIATIONS_ONLY.values():
            for variation in variations:
                self.assertIn(
                    EDITIONS[variation],
                    REPORTERS.keys(),
                    msg="Could not map variation to a valid reporter: %s"
                    % variation,
                )

    def test_basic_names_to_editions(self):
        """Do we get something like we expected in the NAME_TO_EDITION var?"""
        self.assertEqual(
            ["A.", "A.2d", "A.3d"], NAMES_TO_EDITIONS["Atlantic Reporter"]
        )

    def test_editions_ordering(self):
        """Test Ill. App., where we don't have good start dates."""
        self.assertEqual(
            ["Ill. App.", "Ill. App. 2d", "Ill. App. 3d"],
            NAMES_TO_EDITIONS["Illinois Appellate Court Reports"],
        )

    def test_that_all_dates_are_converted_to_dates_not_strings(self):
        """Do we properly make the ISO-8601 date strings into Python dates?"""
        # for reporter_abbv, reporter_list, reporter_data in iter_reporters():
        for e_name, e_dates in iter_editions():
            # e_name == "A. 2d"
            # e_dates == {
            #     "end": "1938-12-31T00:00:00",
            #     "start": "1885-01-01T00:00:00"
            # }
            for key in ["start", "end"]:
                is_date_or_none = (
                    isinstance(e_dates[key], datetime.datetime)
                    or e_dates[key] is None
                )
                self.assertTrue(
                    is_date_or_none,
                    msg=(
                        "%s dates in the reporter '%s' appear to be "
                        "coming through as '%s'"
                        % (key, e_name, type(e_dates[key]))
                    ),
                )
                if key == "start":
                    start_is_not_none = e_dates[key] is not None
                    self.assertTrue(
                        start_is_not_none,
                        msg=(
                            "Start date in reporter '%s' appears to "
                            "be None, not 1750" % e_name
                        ),
                    )

    def test_all_reporters_have_valid_cite_type(self):
        """Do all reporters have valid cite_type values?"""
        for reporter_abbv, reporter_list, reporter_data in iter_reporters():
            self.assertIn(
                reporter_data["cite_type"],
                VALID_CITE_TYPES,
                "%s did not have a valid cite_type value" % reporter_abbv,
            )

    def test_all_required_keys_no_extra_keys(self):
        """Are all required keys present? Are there any keys present that
        shouldn't be?
        """
        required_fields = [
            "cite_type",
            "editions",
            "mlz_jurisdiction",
            "name",
            "variations",
        ]
        optional_fields = [
            "cite_format",
            "publisher",
            "notes",
            "href",
            "regexes",
            "examples",
        ]
        all_fields = required_fields + optional_fields
        for reporter_abbv, reporter_list, reporter_data in iter_reporters():

            # All required fields present?
            for required_field in required_fields:
                try:
                    reporter_data[required_field]
                except KeyError:
                    self.fail(
                        "Reporter '%s' lacks required field '%s'"
                        % (reporter_abbv, required_field)
                    )

            # No extra fields?
            for k in reporter_data.keys():
                self.assertIn(
                    k,
                    all_fields,
                    "Reporter '%s' has an unknown field '%s'"
                    % (reporter_abbv, k),
                )

            # No empty string values?
            for k, v in reporter_data.items():
                if isinstance(v, str):
                    self.assertTrue(
                        v != "",
                        msg="Field '%s' is empty in reporter '%s'"
                        % (k, reporter_abbv),
                    )

    def test_no_variation_is_same_as_key(self):
        """Are any variations identical to the keys they're supposed to be
        variations of?
        """
        for variation, keys in VARIATIONS_ONLY.items():
            for key in keys:
                self.assertNotEqual(
                    variation,
                    key,
                    "The variation '%s' is identical to the key it's supposed "
                    "to be a variation of." % variation,
                )

    def test_fields_tidy(self):
        """Do fields have any messiness?

        For example:
         - some punctuation is not allowed in some keys
         - spaces at beginning/end not allowed
        """

        def cleaner(s):
            return re.sub(r"[^ 0-9a-zA-Z.,\-'&()\[\]]", "", s.strip())

        msg = "Got bad punctuation in: %s"
        for reporter_abbv, reporter_list, reporter_data in iter_reporters():
            self.assertEqual(
                reporter_abbv, cleaner(reporter_abbv), msg=msg % reporter_abbv
            )
            for k in reporter_data["editions"].keys():
                self.assertEqual(cleaner(k), k, msg=msg % k)
            for k, v in reporter_data["variations"].items():
                self.assertEqual(cleaner(k), k, msg=msg % k)
                self.assertEqual(cleaner(v), v, msg=msg % v)

        for s in emit_strings(REPORTERS):
            self.assertEqual(
                s.strip(), s, msg="Fields needs whitespace stripped: '%s'" % s
            )

    def test_nothing_ends_before_it_starts(self):
        """Do any editions have end dates before their start dates?"""
        for k, edition in iter_editions():
            if edition["start"] and edition["end"]:
                self.assertLessEqual(
                    edition["start"],
                    edition["end"],
                    msg="It appears that edition %s ends before it "
                    "starts." % k,
                )

    def test_json_format(self):
        """Does format of reporters.json match json.dumps(json.loads(), sort_keys=True)? """
        for file_name in ("reporters.json", "regexes.json"):
            with self.subTest(file_name=file_name):
                json_path = (
                    Path(__file__).parent / "reporters_db" / "data" / file_name
                )
                json_str = json_path.read_text()
                reformatted = json.dumps(
                    json.loads(json_str),
                    indent=4,
                    ensure_ascii=False,
                    sort_keys=True,
                )
                reformatted += "\n"
                if json_str != reformatted:
                    if os.environ.get("FIX_JSON"):
                        json_path.write_text(reformatted)
                    else:
                        diff = context_diff(
                            json_str.splitlines(),
                            reformatted.splitlines(),
                            fromfile="reporters.json",
                            tofile="expected.json",
                        )
                        self.fail(
                            ("%s needs reformatting. " % file_name)
                            + "Run with env var FIX_JSON=1 to update the file automatically. "
                            + "Diff of actual vs. expected:\n"
                            + "\n".join(diff)
                        )

    def test_regexes(self):
        """Do custom regexes and examples match up?"""
        for reporter_abbv, reporter_list, reporter_data in iter_reporters():
            examples = reporter_data.get("examples", [])
            matched_examples = set()
            custom_regexes = {}

            # check that each custom regex matches at least one example
            for edition_abbv, edition in reporter_data["editions"].items():
                if not edition.get("regexes"):
                    continue
                with self.subTest(
                    "Check edition regexes", edition=edition_abbv
                ):
                    for edition_regex in edition["regexes"]:
                        full_regex = recursive_substitute(
                            edition_regex, REGEX_VARIABLES
                        )
                        regexes = substitute_editions(
                            full_regex,
                            edition_abbv,
                            reporter_data["variations"],
                        )
                        custom_regexes[edition_regex] = regexes
                        has_match = False
                        for example in examples:
                            for regex in regexes:
                                if re.match(regex + "$", example):
                                    has_match = True
                                    matched_examples.add(example)
                                    break
                        if not has_match:
                            try:
                                import exrex

                                candidate = "Possible examples: %s" % [
                                    exrex.getone(regexes[0], limit=3)
                                    for _ in range(10)
                                ]
                            except ImportError:
                                candidate = "Run 'pip install exrex' to generate a candidate example"
                            self.fail(
                                "Reporter '%s' has no match in 'examples' for custom regex '%s'.\nExpanded regexes: %s.\n%s"
                                % (
                                    reporter_abbv,
                                    edition_regex,
                                    regexes,
                                    candidate,
                                )
                            )

            # check that each example is matched by at least one regex
            if custom_regexes:
                with self.subTest(
                    "Check all examples matched by custom regex",
                    reporter=reporter_abbv,
                ):
                    self.assertEqual(
                        set(examples),
                        matched_examples,
                        "Not all examples matched. If custom regexes are provided, all examples should match. Regexes tried: %s"
                        % custom_regexes,
                    )


if __name__ == "__main__":
    import unittest

    unittest.main()
