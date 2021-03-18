import re
from collections import OrderedDict
from string import Template


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
    for reporter_key, data_list in reporters.items():
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
            for edition_key, edition_value in data["editions"].items():
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
    for reporter_key, data_list in reporters.items():
        # For each reporter key...
        for data in data_list:
            # Map the cite_format if it exists
            for edition_key, edition_value in data["editions"].items():
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
    for reporter_key, data_list in reporters.items():
        for data in data_list:
            abbrevs = data["editions"].keys()
            # Sort abbreviations by start date of the edition
            sort_func = lambda x: str(data["editions"][x]["start"]) + x
            abbrevs = sorted(abbrevs, key=sort_func)
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
        variables[k + "_optional"] = "(?:%s ?)?" % v

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
    for i in range(max_depth):
        new_val = Template(old_val).safe_substitute(variables)
        if new_val == old_val:
            break
        old_val = new_val
    else:
        raise ValueError("max_depth exceeded for template '%s'" % template)
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
