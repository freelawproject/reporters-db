# Version History

## Future Versions

 - All dates are dialed in to the nearest year for every edition of
   every reporter (some still require research beyond what Blue Book
   provides). See `issue #7 <https://github.com/freelawproject/reporters-db/issues/7>`__
 - All dates are dialed into the correct day for every edition of
   every reporter.
 - International Reporters added?
 - Other features (suggestions welcome)?

## Current Version

 - 3.2.0 (2021-05-26): Adds federal administrative and executive materials. Adds U.S.C. to laws parsers.  

## Past Versions

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









