# Version History

## Future Versions

 - All dates are dialed in to the nearest year for every edition of
   every reporter (some still require research beyond what Blue Book
   provides). See `issue #7 <https://github.com/freelawproject/reporters-db/issues/7>`__
 - All dates are dialed into the correct day for every edition of
   every reporter.
 - International Reporters added?
 - Other features (suggestions welcome)?

## Upcoming Changes

- N/A

## Current Version

 - 3.2.17 (2022-02-07): Update NY Reports.

## Past Versions

 - 3.2.16 (2022-02-07): Historical NY reporters (2) added.

 - 3.2.15 (2022-02-02): Update regexes for a handful of old NY reporters.

 - 3.2.14 (2022-01-14): Add Kelly Reporter (GA), Update variations for I & N Dec. and update Oregon variations for historical citations.

 - 3.2.13 (2022-01-11): Add Cal Super Ct Reporter.

 - 3.2.12 (2022-01-11): Add various additional NY reporters from 1800s

 - 3.2.11 (2022-01-10): Add California and New York Reporters with various updates.  Including Coffey, Myrick and Cal. Dist. Ct.

 - 3.2.10 (2022-01-07): Update Arkansas regex to remove potential overlap between editions.

 - 3.2.9 (2022-01-06): Update Arkansas / Appellate Reports. Include regex patterns.

 - 3.2.8 (2022-01-05): Fix Arkansas Appellate Reports.  Divide into two editions. Book edition and neutral online edition.

 - 3.2.7 (2022-01-05): Fix Arkansas Reports.  Divide into two editions. Book edition and neutral online edition.

 - 3.2.2 (2021-06-30): Add F.4th and increment the doomsday clock one notch.

 - 3.2.1 (2021-06-04): Fixes bug with format of journals and adds json schemas to prevent regressions

 - 3.2.0 (2021-05-26): Adds federal administrative and executive materials. Adds U.S.C. to laws parsers.

 - 3.1.x: In addition to several regex enhancements, this version brings two new data files. The first file, `laws.json` provides regular expressions for parsing various state laws. The second, `journals.json` does the same for various law journals.

 Similar our existing data files, these two data files can be imported with `from reporters_db import LAWS, JOURNALS`.

 - 3.0.1: Various improvements to regular expressions

 - 3.0.0: New approach to regexes matches for non-standard reporters (see: `PR #38 <https://github.com/freelawproject/reporters-db/pull/38>`_). Notably, the ``cite_format`` and ``regexes`` fields have been removed from the root reporter object and have been replaced by ``regexes`` and ``examples`` nodes under the ``editions`` key. This allows us to create more granular per-edition examples and regexes.

    We are unaware of any usage of the old keys and they were a beta-quality feature, so we are removing them and moving forward. Get in touch if our assumptions here are wrong.

 - 2.0.7: Merges in main reporters from Harvard's LIL. Migrates to Github Actions from Travis.

 - 2.0.0: Adds 273 additional reporters, 443 new variations, and 301 new editions

 - 1.0.20: Adds tax courts

 - 1.0.13: Updates the case name abbreviations

 - 1.0.9: Updates the mlz\_jurisdiction field to be state-specific, per
   issue #1.

 - 1.0.2

   1. Adds tests to verify the data (see ./tests.py)
   2. Fixes a few data issues after applying tests

 - 1.0.1

   1. Bug fix after application to Lawbox bulk data
   2. Updates cite\_type for better granularity and to eliminate a few
      errors.
   3. Adds WL, LEXIS and U.S. App. LEXIS as specialty\_lexis and
      specialty\_west cite\_types.
   4. ``fed`` cite\_type has been converted to ``federal``

 - 1.0: Has all common Blue Book reporters, with their variations from
   the Cardiff database.









