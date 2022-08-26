import datetime
import json
import os

from .utils import (
    names_to_abbreviations,
    process_variables,
    suck_out_editions,
    suck_out_formats,
    suck_out_variations_only,
)


def datetime_parser(dct):
    for k, v in dct.items():
        if k in ("start", "end") and v is not None:
            dct[k] = datetime.datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
    return dct


db_root = os.path.dirname(os.path.realpath(__file__))
with open(
    os.path.join(db_root, "data", "reporters.json"), encoding="utf-8"
) as f:
    REPORTERS = json.load(f, object_hook=datetime_parser)

with open(
    os.path.join(db_root, "data", "state_abbreviations.json"), encoding="utf-8"
) as f:
    STATE_ABBREVIATIONS = json.load(f)

with open(
    os.path.join(db_root, "data", "case_name_abbreviations.json"),
    encoding="utf-8",
) as f:
    CASE_NAME_ABBREVIATIONS = json.load(f)

with open(os.path.join(db_root, "data", "laws.json"), encoding="utf-8") as f:
    LAWS = json.load(f, object_hook=datetime_parser)

with open(
    os.path.join(db_root, "data", "journals.json"), encoding="utf-8"
) as f:
    JOURNALS = json.load(f, object_hook=datetime_parser)

with open(
    os.path.join(db_root, "data", "regexes.json"), encoding="utf-8"
) as f:
    RAW_REGEX_VARIABLES = json.load(f)
    REGEX_VARIABLES = process_variables(RAW_REGEX_VARIABLES)

VARIATIONS_ONLY = suck_out_variations_only(REPORTERS)
EDITIONS = suck_out_editions(REPORTERS)
NAMES_TO_EDITIONS = names_to_abbreviations(REPORTERS)
SPECIAL_FORMATS = suck_out_formats(REPORTERS)
