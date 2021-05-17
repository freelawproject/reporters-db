import json
import os
import re
import datetime
from difflib import context_diff
from pathlib import Path
from string import Template

import six
from reporters_db import (
    REPORTERS,
    VARIATIONS_ONLY,
    EDITIONS,
    NAMES_TO_EDITIONS,
    REGEX_VARIABLES,
    LAWS,
    JOURNALS,
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


class BaseTestCase(TestCase):
    def check_regexes(self, regexes, examples):
        """Check that each regex matches at least one example, and each example matches at least one regex.
        regexes should be a list of [(regex_template, regex)]."""
        matched_examples = set()

        # check that each regex matches at least one example
        for regex_template, regex in regexes:
            has_match = False
            for example in examples:
                if re.match(regex + "$", example):
                    has_match = True
                    matched_examples.add(example)
            if not has_match:
                try:
                    import exrex

                    candidate = "Possible examples: %s" % [
                        exrex.getone(regex, limit=3) for _ in range(10)
                    ]
                except ImportError:
                    candidate = "Run 'pip install exrex' to generate a candidate example"
                self.fail(
                    "No match in 'examples' for custom regex '%s'.\n"
                    "Expanded regex: %s.\n"
                    "Provided examples: %s.\n"
                    "%s"
                    % (
                        regex_template,
                        regex,
                        examples,
                        candidate,
                    )
                )

        # check that each example is matched by at least one regex
        self.assertEqual(
            set(examples),
            matched_examples,
            "Not all examples matched. If custom regexes are provided, all examples should match."
            "Unmatched examples: %s. Regexes tried: %s"
            % (set(examples) - matched_examples, regexes),
        )

    def check_json_format(self, file_name):
        """Does format of json file match json.dumps(json.loads(), sort_keys=True)?"""
        json_path = Path(__file__).parent / "reporters_db" / "data" / file_name
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

    def check_dates(self, start, end):
        """Check that start and end dates are valid."""
        if start is not None:
            self.assertTrue(
                isinstance(start, datetime.datetime),
                f"{repr(start)} should be imported as a date.",
            )
        if end is not None:
            self.assertTrue(
                isinstance(end, datetime.datetime),
                f"{repr(end)} should be imported as a date.",
            )
        if start is not None and end is not None:
            self.assertLessEqual(start, end)

    def check_ascii(self, obj):
        """Check that all strings in obj match a list of expected ascii characters."""
        allowed_chars = r"[ 0-9a-zA-Z.,\-'&(){}\[\]\\$§_?<>+:/]"
        for s in emit_strings(obj):
            remaining_chars = re.sub(allowed_chars, "", s)
            self.assertFalse(
                remaining_chars,
                f"Unexpected characters in {repr(s)}: {repr(remaining_chars)}.",
            )

    def check_whitespace(self, obj):
        for s in emit_strings(obj):
            self.assertEqual(
                s.strip(), s, msg="Field needs whitespace stripped: '%s'" % s
            )
            non_space_whitespace = any(w != " " for w in re.findall(r"\s+", s))
            self.assertFalse(
                non_space_whitespace,
                f"Field has unexpected whitespace: {repr(s)}",
            )


class RegexesTest(BaseTestCase):
    """Tests for regexes.json"""

    def text_json_format(self):
        self.check_json_format("regexes.json")


class ReportersTest(BaseTestCase):
    """Tests for reporters.json"""

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

    def test_dates(self):
        """Do we properly make the ISO-8601 date strings into Python dates?"""
        # for reporter_abbv, reporter_list, reporter_data in iter_reporters():
        for edition_name, edition in iter_editions():
            self.check_dates(edition["start"], edition["end"])

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
        """Check that fields don't have unexpected characters or whitespace."""
        for reporter_abbv, reporter_list, reporter_data in iter_reporters():
            self.check_ascii(reporter_abbv)
            self.check_ascii(list(reporter_data["editions"].keys()))
            self.check_ascii(reporter_data["variations"])

        self.check_whitespace(REPORTERS)

    def test_regexes(self):
        """Do custom regexes and examples match up?"""
        for reporter_abbv, reporter_list, reporter_data in iter_reporters():

            # get list of expanded regexes and examples for this reporter
            examples = reporter_data.get("examples", [])
            regexes = []
            for edition_abbv, edition in reporter_data["editions"].items():
                if not edition.get("regexes"):
                    continue
                for regex_template in edition["regexes"]:
                    edition_strings = [edition_abbv] + [
                        k
                        for k, v in reporter_data["variations"].items()
                        if v == edition_abbv
                    ]
                    regex = recursive_substitute(
                        regex_template, REGEX_VARIABLES
                    )
                    regex = Template(regex).safe_substitute(
                        edition="(?:%s)"
                        % "|".join(re.escape(e) for e in edition_strings)
                    )
                    regexes.append((regex_template, regex))

            if not regexes:
                continue

            with self.subTest(
                "Check reporter regexes", reporter=reporter_abbv
            ):
                self.check_regexes(regexes, examples)

    def text_json_format(self):
        self.check_json_format("reporters.json")


class LawsTest(BaseTestCase):
    """Tests for laws.json"""

    @staticmethod
    def iter_laws():
        for law_key, law_list in LAWS.items():
            yield from ((law_key, law) for law in law_list)

    def test_regexes(self):
        """Do custom regexes and examples match up?"""
        for law_key, law in self.iter_laws():
            regexes = []
            # expand regex and substitute $edition value
            series_strings = [law_key] + law["variations"]
            for regex_template in law["regexes"]:
                regex = recursive_substitute(regex_template, REGEX_VARIABLES)
                regex = Template(regex).safe_substitute(
                    edition="(?:%s)"
                    % "|".join(re.escape(e) for e in series_strings)
                )
                regexes.append((regex_template, regex))
            with self.subTest("Check law regexes", name=law["name"]):
                self.check_regexes(regexes, law["examples"])

    def test_json_format(self):
        self.check_json_format("laws.json")

    def test_dates(self):
        for law_key, law in self.iter_laws():
            self.check_dates(law["start"], law["end"])

    def test_fields_tidy(self):
        """Check that fields don't have unexpected characters or whitespace."""
        for law_key, law in self.iter_laws():
            self.check_ascii(law["regexes"])
            self.check_ascii(law["examples"])

        self.check_whitespace(REPORTERS)


class JournalsTest(BaseTestCase):
    """Tests for journals.json"""

    @staticmethod
    def iter_journals():
        for journal_key, journal_list in JOURNALS.items():
            yield from ((journal_key, journal) for journal in journal_list)

    def test_regexes(self):
        """Do custom regexes and examples match up?"""
        for journal_key, journal in self.iter_journals():
            regexes = [
                (
                    regex_template,
                    recursive_substitute(regex_template, REGEX_VARIABLES),
                )
                for regex_template in journal.get("regexes", [])
            ]
            with self.subTest("Check journal regexes", name=journal["name"]):
                self.check_regexes(regexes, journal.get("examples", []))

    def text_json_format(self):
        self.check_json_format("journals.json")

    def test_dates(self):
        for journal_key, journal in self.iter_journals():
            self.check_dates(journal["start"], journal["end"])

    def test_fields_tidy(self):
        """Check that fields don't have unexpected characters or whitespace."""
        for journal_key, journal in self.iter_journals():
            self.check_ascii(journal_key)
            self.check_ascii(journal["name"])

        self.check_whitespace(JOURNALS)


if __name__ == "__main__":
    import unittest

    unittest.main()
