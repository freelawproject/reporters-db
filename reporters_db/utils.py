import json
import re
from collections import OrderedDict
from pathlib import Path
from string import Template
from typing import Optional


def suck_out_variations_only(reporters):
    """Builds a dictionary of variations to canonical reporters.

    The dictionary takes the form of:
        {
         "A. 2d": ["A.2d"],
         ...
         "P.R.": ["Pen. & W.", "P.R.R.", "P."],
        }

    In other words, it's a dictionary that maps each variation to a list of
    reporters that it could be possibly referring to.
    """
    variations_out = {}
    for _reporter_key, data_list in reporters.items():
        # For each reporter key...
        for data in data_list:
            # For each book it maps to...
            for variation_key, variation_value in data["variations"].items():
                try:
                    variations_list = variations_out[variation_key]
                    if variation_value not in variations_list:
                        variations_list.append(variation_value)
                except KeyError:
                    # The item wasn't there; add it.
                    variations_out[variation_key] = [variation_value]

    return variations_out


def suck_out_editions(reporters):
    """Builds a dictionary mapping edition keys to their root name.

    The dictionary takes the form of:
        {
         "A.":   "A.",
         "A.2d": "A.",
         "A.3d": "A.",
         "A.D.": "A.D.",
         ...
        }

    In other words, this lets you go from an edition match to its parent key.
    """
    editions_out = {}
    for reporter_key, data_list in reporters.items():
        # For each reporter key...
        for data in data_list:
            # For each book it maps to...
            for edition_key, _edition_value in data["editions"].items():
                try:
                    editions_out[edition_key]
                except KeyError:
                    # The item wasn't there; add it.
                    editions_out[edition_key] = reporter_key
    return editions_out


def suck_out_formats(reporters):
    """Builds a dictionary mapping edition keys to their cite_format if any.

    The dictionary takes the form of:
        {
            'T.C. Summary Opinion': '{reporter} {volume}-{page}',
            'T.C. Memo.': '{reporter} {volume}-{page}'
            ...
        }

    In other words, this lets you go from an edition match to its parent key.
    """
    formats_out = {}
    for _reporter_key, data_list in reporters.items():
        # For each reporter key...
        for data in data_list:
            # Map the cite_format if it exists
            for edition_key, _edition_value in data["editions"].items():
                try:
                    formats_out[edition_key] = data["cite_format"]
                except KeyError:
                    # The item wasn't there; add it.
                    pass
    return formats_out


def names_to_abbreviations(reporters):
    """Build a dict mapping names to their variations

    Something like:

        {
            "Atlantic Reporter": ['A.', 'A.2d'],
        }

    Note that the abbreviations are sorted by start date.
    """
    names = {}
    for _reporter_key, data_list in reporters.items():
        for data in data_list:
            abbrevs = data["editions"].keys()
            # Sort abbreviations by start date of the edition
            abbrevs = sorted(
                abbrevs, key=lambda x: str(data["editions"][x]["start"]) + x
            )
            names[data["name"]] = abbrevs
    sorted_names = OrderedDict(sorted(names.items(), key=lambda t: t[0]))
    return sorted_names


def process_variables(variables):
    r"""Process contents of variables.json, in preparation for passing to recursive_substitute:

    - Strip keys ending in '#', which are treated as comments
    - Flatten nested dicts, so {"page": {"": "A", "foo": "B"}} becomes {"page": "A", "page_foo": "B"}
    - Add optional variants for each key, so {"page": "\d+"} becomes {"page_optional": "(?:\d+ ?)?"}
    - Resolve nested references
    """

    # flatten variables and remove comments
    def flatten(d, parent_key=""):
        items = {}
        for k, v in d.items():
            if k.endswith("#"):
                continue
            new_key = "_".join(i for i in (parent_key, k) if i)
            if isinstance(v, dict):
                items.update(flatten(v, new_key))
            else:
                items[new_key] = v
        return items

    variables = flatten(variables)

    # add optional variables
    for k, v in list(variables.items()):
        variables[f"{k}_optional"] = f"(?:{v} ?)?"

    # resolve references
    variables = {
        k: recursive_substitute(v, variables) for k, v in variables.items()
    }

    return variables


def recursive_substitute(template, variables, max_depth=100):
    """Recursively substitute values in `template` from `variables`. For example:
        >>> recursive_substitute("$a $b $c", {'a': '$b', 'b': '$c', 'c': 'foo'})
        "foo foo foo"
    Infinite loops will raise a ValueError after max_depth loops.
    """
    old_val = template
    for _ in range(max_depth):
        new_val = Template(old_val).safe_substitute(variables)
        if new_val == old_val:
            break
        old_val = new_val
    else:
        raise ValueError(f"max_depth exceeded for template '{template}'")
    return new_val


def substitute_edition(regex, edition_name):
    """Insert edition_name in place of $edition."""
    return Template(regex).safe_substitute(edition=re.escape(edition_name))


def substitute_editions(regex, edition_name, variations):
    r"""Insert edition strings for the given edition into a regex with an $edition placeholder. Example:
    >>> substitute_editions(r'\d+ $edition \d+', 'Foo.', {'Foo. Var.': 'Foo.'})
    "\\d+ (?:Foo\\.|Foo\\. Var\\.) \d+"
    """
    if "$edition" not in regex and "${edition}" not in regex:
        return [regex]
    edition_strings = [edition_name] + [
        k for k, v in variations.items() if v == edition_name
    ]
    return [substitute_edition(regex, e) for e in edition_strings]


def load_reporters() -> dict:
    """Load the reporters.json data."""
    data_path = Path(__file__).parent / "data" / "reporters.json"
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)


def get_volume_ranges() -> dict[str, tuple[int, int]]:
    """Get volume ranges for all reporters with range data.

    Returns:
        Dictionary mapping reporter abbreviation to (min, max) tuple.

    Example:
        >>> ranges = get_volume_ranges()
        >>> ranges["U.S."]
        (1, 606)
    """
    reporters = load_reporters()
    ranges = {}

    for _reporter_key, reporter_list in reporters.items():
        for reporter in reporter_list:
            for edition_key, edition_data in reporter.get(
                "editions", {}
            ).items():
                if volume_range := edition_data.get("volume_range"):
                    ranges[edition_key] = (
                        volume_range["min"],
                        volume_range["max"],
                    )

    return ranges


def get_volume_range(reporter: str) -> Optional[tuple[int, int]]:
    """Get the volume range for a specific reporter.

    Args:
        reporter: Reporter abbreviation (e.g., "U.S.", "F.2d")

    Returns:
        Tuple of (min_volume, max_volume) or None if not found.

    Example:
        >>> get_volume_range("U.S.")
        (1, 606)
        >>> get_volume_range("Unknown Reporter")
        None
    """
    ranges = get_volume_ranges()
    return ranges.get(reporter)


def is_volume_valid(
    reporter: str,
    volume: int,
    tolerance_multiplier: float = 1.5,
) -> tuple[bool, str]:
    """Check if a volume number is valid for a reporter.

    Args:
        reporter: Reporter abbreviation
        volume: Volume number to validate
        tolerance_multiplier: Multiplier for max volume to allow new volumes

    Returns:
        Tuple of (is_valid, reason). If valid, reason is empty string.

    Example:
        >>> is_volume_valid("U.S.", 500)
        (True, "")
        >>> is_volume_valid("U.S.", 5000)
        (False, "Volume 5000 exceeds maximum 909 for U.S.")
    """
    volume_range = get_volume_range(reporter)

    if volume_range is None:
        # No data for this reporter, assume valid
        return True, ""

    min_vol, max_vol = volume_range
    max_with_tolerance = int(max_vol * tolerance_multiplier)

    if volume < min_vol:
        return (
            False,
            f"Volume {volume} is below minimum {min_vol} for {reporter}",
        )

    if volume > max_with_tolerance:
        return (
            False,
            f"Volume {volume} exceeds maximum {max_with_tolerance} for {reporter}",
        )

    return True, ""


def uses_year_as_volume(reporter: str) -> bool:
    """Check if a reporter uses publication year as volume number.

    Some reporters (like neutral citations) use the year as volume.
    These need different validation logic.

    Args:
        reporter: Reporter abbreviation

    Returns:
        True if this reporter uses year as volume, False otherwise.
    """
    reporters = load_reporters()

    for _reporter_key, reporter_list in reporters.items():
        for reporter_data in reporter_list:
            for edition_key, edition_data in reporter_data.get(
                "editions", {}
            ).items():
                if edition_key == reporter:
                    volume_range = edition_data.get("volume_range", {})
                    return volume_range.get("uses_year", False)

    return False
