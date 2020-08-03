
from collections import OrderedDict


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


