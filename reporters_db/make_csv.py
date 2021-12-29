"""This will take the reporters json file and flatten it into a CSV."""

import csv

from reporters_db import REPORTERS

FIELDNAMES = [
    "citation",
    "name",
    "publisher",
    "cite_type",
    "edition1",
    "edition2",
    "edition3",
    "edition4",
    "edition5",
    "edition6",
    "start_e1",
    "start_e2",
    "start_e3",
    "start_e4",
    "start_e5",
    "start_e6",
    "end_e1",
    "end_e2",
    "end_e3",
    "end_e4",
    "end_e5",
    "end_e6",
    "mlz_jurisdictions",
    "variations",
    "href",
    "notes",
]


def make_editions_dict(editions):
    """Take a reporter editions dict and flatten it, returning a dict for
    use in the DictWriter.
    """
    d = {}
    nums = ["1", "2", "3", "4", "5", "6"]
    num_counter = 0
    for k, date_dict in editions.items():
        d[f"edition{nums[num_counter]}"] = k
        if date_dict["start"] is not None:
            d[f"start_e{nums[num_counter]}"] = date_dict["start"].isoformat()
        if date_dict["end"] is not None:
            d[f"end_e{nums[num_counter]}"] = date_dict["end"].isoformat()

        num_counter += 1

    return d


def make_csv():
    with open("reporters.csv", "w") as f:
        out = csv.DictWriter(f, fieldnames=FIELDNAMES)
        out.writeheader()

        for cite, reporter_list in REPORTERS.items():
            print(f"Adding: {cite}")
            for reporter in reporter_list:
                d = make_editions_dict(reporter["editions"])
                d["citation"] = cite
                d["name"] = reporter["name"]
                d["publisher"] = reporter.get("publisher", "")
                d["cite_type"] = reporter["cite_type"]
                d["mlz_jurisdictions"] = ", ".join(
                    reporter["mlz_jurisdiction"]
                )
                d["variations"] = ", ".join(reporter["variations"].keys())
                d["href"] = reporter.get("href", "")
                d["notes"] = reporter.get("notes", "")

                out.writerow(d)


if __name__ == "__main__":
    make_csv()
