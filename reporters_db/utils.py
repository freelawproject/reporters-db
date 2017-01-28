import json
import datetime


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


def print_json_with_dates(obj):
    date_handler = lambda obj: (
        obj.isoformat()
        if isinstance(obj, datetime.datetime)
        or isinstance(obj, datetime.date)
        else None)

    print(json.dumps(obj, default=date_handler, sort_keys=True))
