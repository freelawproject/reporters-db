+---------------+---------------------+-------------------+
| |Lint Badge|  | |Test Badge|        |  |Version Badge|  |
+---------------+---------------------+-------------------+

.. |Lint Badge| image:: https://github.com/freelawproject/reporters-db/workflows/Lint/badge.svg
.. |Test Badge| image:: https://github.com/freelawproject/reporters-db/workflows/Tests/badge.svg
.. |Version Badge| image:: https://badge.fury.io/py/reporters-db.svg

Background of the Free Law Reporters Database
=============================================

A long, long time ago near a courthouse not too far away, people started
keeping books of every important opinion that was ever written. These
books became known as *reporters* and were generally created by
librarian-types of yore such as `Mr. William
Cranch <https://en.wikipedia.org/wiki/William_Cranch>`__ and `Alex
Dallas <https://en.wikipedia.org/wiki/Alexander_J._Dallas_%28statesman%29>`__.

These people were busy for the next few centuries and created
*thousands* of these books, culminating in what we know today as West's
reporters or as regional reporters like the "Dakota Reports" or the
thoroughly-named, "Synopses of the Decisions of the Supreme Court of
Texas Arising from Restraints by Conscript and Other Military
Authorities (Robards)."

In this repository we've taken a look at all these reporters and tried
to sort out what we know about them and convert that to data. This data
is available as a JSON file, as Python variables, and can be browsed in an
unofficial CSV (it's usually out of date).

Naturally, converting several centuries' history into clean data results
in a mess, but we've done our best and this mess is in use in a number
of projects as listed below. As of version 2.0, this data contains information
about 733 reporters, including 1,466 name variations, and 830 editions.

We hope you'll find this useful to your endeavors and that you'll share
your work with the community if you improve or use this work.


Data Sourcing
=============

This project has been enhanced several times with data from several sources:

1. The original data came from parsing the citation fields for millions of cases in CourtListener.

2. A second huge push came from parsing metadata obtained from two major legal publishers, and by parsing the citation fields of Havard's Case.law database.

3. An audit was performed and additional fields were added by using regular expressions to find number-word-number strings in the entire Harvard Case.law database. The results of this were sorted by frequency, with the top omissions fixed.

Along the way, small and subdry improvements have been made as gaps were identified and fixed.

The result is that this database should thus be very complete when it comes to reporter abbreviations and variations. It has the data from CourtListener, two major legal publishers, and Harvard's Case.law. Hundreds of hours have gone into this database to make it complete.

CSV
===

You can make a CSV of this data by running:

::

    make_csv.py

We keep a copy of this CSV in this repository (``reporters.csv``), but
it is not kept up to date. It should, however, provide a good idea of
what's here.


Known Implementations
=====================

1. This work was originally deployed in the
   `CourtListener <https://www.courtlistener.com>`__ citation finder
   beginning in about 2012. It has been used literally millions of times
   to identify citations between cases.

2. An extension for Firefox known as the `Free Law
   Ferret <http://citationstylist.org/2013/08/20/free-law-ferret-document-to-cited-cases-in-a-click/>`__
   uses this code to find citations in your browser as you read things
   -- all over the Web.

3. A Node module called
   `Walverine <https://github.com/adelevie/walverine>`__ uses an
   iteration of this code to find citations using the V8 JavaScript
   engine.

Additional usages can be `found via Github <https://github.com/freelawproject/reporters-db/network/dependents?package_id=UGFja2FnZS01MjU0MTgzNg%3D%3D>`__.


Some Notes on the Data
======================

Some things to bear in mind as you are examining the Free Law Reporters
Database:

1. Each Reporter key maps to a list of reporters that that key can
   represent. In some cases (especially in early reporters), the key is
   ambiguous, referring to more than one possible reporter.

2. Formats follow the Blue Book standard, with variations listed for
   local rules and other ways lawyers abbreviate it over the years or
   accidentally.

3. The ``variations`` key consists of data from local rules, found
   through organic usage in our corpus and from the `Cardiff Index to
   Legal Abbreviations <http://www.legalabbrevs.cardiff.ac.uk/>`__. We
   have used a dict for these values due to the fact that there can be
   variations for each series.

4. ``mlz_jurisdiction`` corresponds to the work that is being done for
   Multi-Lingual Zotero. This field is maintained by Frank Bennett and
   may sometimes be missing values.

5. Some reporters have ``href`` or ``notes`` fields to provide a link to
   the best available reference (often Wikipedia) or to provide notes
   about the reporter itself.

6. Regarding dates of the editions, there are a few things to know. In
   reporters with multiple series, if multiple volumes have the same
   dates, this indicates that the point where one series ends and the
   other begins is unknown. If an edition has 1750 as its start date,
   this indicates that the actual start date is unknown. Likewise, if an
   edition has ``null`` as its end date, that indicates the actual end
   date is either unknown, or it's known that the series has not
   completed. These areas need research before we can release version
   1.1 of this database. Finally, dates are inclusive, so the first and
   last opinions in a reporter series have the same dates as the
   database.


A complete data point has fields like so:

::

    "$citation": [
        {
            "cite_type": "state|federal|neutral|specialty|specialty_west|specialty_lexis|state_regional|scotus_early",
            "editions": {
                "$citation": {
                    "end": null,
                    "regexes": [],
                    "start": "1750-01-01T00:00:00"
                },
                "$citation 2d": {
                    "end": null,
                    "regexes": [],
                    "start": "1750-01-01T00:00:00"
                }
            },
            "examples": [],
            "mlz_jurisdiction": [],
            "name": "",
            "variations": {},
            "notes": "",
            "href": "",
            "publisher": ""
        }
    ],

The "regexes" field and regexes.json placeholders
-------------------------------------------------

The "regexes" field can contain raw regular expressions to match a custom citation format,
or can contain placeholders to be substituted from ``regexes.json`` using
`python Template formatting <https://docs.python.org/3/library/string.html#template-strings>`__.

If custom regexes are provided, the tests will require that all regexes match at least one
example in ``examples`` and that all examples match at least one regex.

When adding a new regex it can be useful to ``pip install exrex`` and run the tests *without*
adding any examples to get a listing of potential citations that would be matched by the new
regex.


``state_abbreviations`` and ``case_name_abbreviations`` files
-------------------------------------------------------------

1. Abbreviations are based on data from the values in the nineteenth
   edition of the Blue Book supplemented with abbreviations found in our
   corpus.
2. ``case_name_abbreviations.json`` contains the abbreviations that are
   likely to occur in the case name of an opinion.
3. ``state_abbreviations.json`` contains the abbreviations that are
   likely to be used to refer to American states.

Notes on Specific Data Point and References
-------------------------------------------

1. A good way to look up abbreviations is in `Prince's Bieber Dictionary
   of Legal Abbreviations <https://books.google.com/books?id=4aJsAwAAQBAJ&dq=%22Ohio+Law+Rep.%22&source=gbs_navlinks_s>`__. You can find a lot of this book on Google Books,
   but we have it as a PDF too. Just ask.

2. Mississippi supports neutral citations, but does so in their own
   format, as specified in `this
   rule <http://www.aallnet.org/main-menu/Advocacy/access/citation/neutralrules/rules-ms.html>`__.
   Research is needed for the format in ``reporters.json`` to see if it
   is used accidentally as a variant of their rule or whether it is an
   error in this database.

3. New Mexico dates confirmed via the `table
   here <http://www.nmcompcomm.us/nmcases/pdf/NM%20Reports%20to%20Official%20-%20Vols.%201-75.pdf>`__.

4. Both Puerto Rico and "Pennsylvania State Reports, Penrose and Watts"
   use the citation "P.R."


Installation (Python)
=====================

You can install the Free Law Reporters Database with a few simple
commands:

::

    pip install reporters-db

Once installed you can use it in your code with something like:

::

    from reporters_db import REPORTERS

You can see all of the variables that can be imported by looking in
``__init__.py``. Other variables currently include:
``STATE_ABBREVIATIONS``, ``CASE_NAME_ABBREVIATIONS``, ``SPECIAL_FORMATS``,
``VARIATIONS_ONLY``, and ``EDITIONS``. These latter two are convenience
variables that you can use to get different views of the ``REPORTERS``
data.

Of course, if you're not using Python, the data is in the ``json``
format, so you should be able to import it using your language of
choice.


Tests
=====

We have a few tests that make sure things haven't completely broken.
They are automatically run by Travis CI each time a push is completed
and should be run by developers as well before pushing. They can be run
with:

::

    python tests.py

It's pretty simple, right?


Version History
===============

Past Versions
-------------

-  1.0: Has all common Blue Book reporters, with their variations from
   the Cardiff database.
-  1.0.1

   1. Bug fix after application to Lawbox bulk data
   2. Updates cite\_type for better granularity and to eliminate a few
      errors.
   3. Adds WL, LEXIS and U.S. App. LEXIS as specialty\_lexis and
      specialty\_west cite\_types.
   4. ``fed`` cite\_type has been converted to ``federal``

-  1.0.2

   1. Adds tests to verify the data (see ./tests.py)
   2. Fixes a few data issues after applying tests

-  1.0.9: Updates the mlz\_jurisdiction field to be state-specific, per
   issue #1.

- 1.0.13: Updates the case name abbreviations

- 1.0.20: Adds tax courts

- 2.0.0: Adds 273 additional reporters, 443 new variations, and 301 new editions

- 2.0.7: Merges in main reporters from Harvard's LIL. Migrates to Github Actions from Travis.


Current Version
---------------

- 3.0.0: New approach to regexes matches for non-standard reporters (see: `PR #38 <https://github.com/freelawproject/reporters-db/pull/38>`_). Notably, the ``cite_format`` and ``regexes`` fields have been removed from the root reporter object and have been replaced by ``regexes`` and ``examples`` nodes under the ``editions`` key. This allows us to create more granular per-edition examples and regexes.

  We are unaware of any usage of the old keys and they were a beta-quality feature, so we are removing them and moving forward. Get in touch if our assumptions here are wrong.


Future Versions
---------------

-  All dates are dialed in to the nearest year for every edition of
   every reporter (some still require research beyond what Blue Book
   provides). See `issue
   #7 <https://github.com/freelawproject/reporters-db/issues/7>`__
-  All dates are dialed into the correct day for every edition of
   every reporter.
-  International Reporters added?
-  Other features (suggestions welcome)?


Releases
--------

Update setup.py, add a git tag to the commit with the version number, and push
to master. Be sure you have your tooling set up to push git tags. That's often
not the default. Github Actions will push a release to PyPi if tests pass.


License
=======

This repository is available under the permissive BSD license, making it
easy and safe to incorporate in your own libraries.

Pull and feature requests welcome. Online editing in Github is possible
(and easy!)
