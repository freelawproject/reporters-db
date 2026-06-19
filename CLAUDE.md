# CLAUDE.md

## Adding a new reporter (or variation)

Reporters live in `reporters_db/data/reporters.json`. The top-level key is the
canonical Blue Book citation abbreviation; its value is a **list** of reporter
objects (a list because the same abbreviation can refer to more than one
reporter historically).

### Data shape

```json
"Citation Abbrev.": [
    {
        "cite_type": "federal",
        "editions": {
            "Citation Abbrev.": { "start": "1750-01-01T00:00:00", "end": null, "regexes": [] }
        },
        "examples": ["12 Citation Abbrev. 432"],
        "variations": { "Citation Abbrev": "Citation Abbrev." },
        "mlz_jurisdiction": ["us;federal"],
        "name": "Full Name Of The Reporter",
        "href": "https://...",        // optional
        "notes": "...",               // optional
        "publisher": "..."            // optional
    }
]
```

### Rules

- **Required fields:** `cite_type`, `editions`, `mlz_jurisdiction`, `name`, `variations`.
- **`cite_type`** must be one of: `federal`, `neutral`, `scotus_early`,
  `specialty`, `specialty_west`, `specialty_lexis`, `state`, `state_regional`.
- **Editions:** every reporter must have an edition keyed by the reporter's own
  abbreviation (the top-level key must appear in `editions`). Multiple series go
  here (e.g. `A.`, `A.2d`, `A.3d`).
- **Dates:** ISO-8601 datetimes or `null`. `1750-01-01` = unknown start; `null`
  end = unknown/ongoing. `start <= end`.
- **Variations:** a dict mapping the variant string → the canonical edition key.
  A variation must **not** equal the key it maps to, and must map to an edition
  that exists.
- **Do not add whitespace-only variations.** Forms that differ from an existing
  abbreviation *only* in inter-token spacing (e.g. `N. Y. S. 2d` vs `N.Y.S.2d`,
  `F. R. D.` vs `F.R.D.`) are handled downstream by eyecite, which makes
  inter-token whitespace optional while keeping periods mandatory (see
  [eyecite#307](https://github.com/freelawproject/eyecite/pull/307)). Only add
  variations that differ in *spelling* (e.g. `App. Div.` → `A.D.`) or
  punctuation, not in spacing alone.
- **Examples:** required only if custom `regexes` are provided. If regexes exist,
  every regex must match at least one example and every example must match at
  least one regex.
- **Field hygiene:** strings are ASCII-ish (see allowed chars in `tests.py`),
  trimmed, no non-space whitespace.

### Regexes (optional)

The `regexes` list (per edition) holds raw regexes or placeholders substituted
from `reporters_db/data/regexes.json` (Python `Template` syntax), e.g.
`"$full_cite"`, `"$volume $reporter $page"`. Each regex must expose named
`<reporter>` and `<page>` groups. Tip: `pip install exrex` and run tests with no
examples to see what a new regex would match.

### Workflow

1. Branch off `main`, named `<issue>-<court-id>-variation` (e.g. `257-bia-variation`).
2. Edit `reporters_db/data/reporters.json`. Keep keys sorted — JSON must equal
   `json.dumps(..., indent=4, ensure_ascii=False, sort_keys=True)`. Run tests
   with `FIX_JSON=1` to auto-reformat.
3. Add a one-line entry under **Upcoming Changes** in `CHANGES.md`. Do **not**
   bump the version in `pyproject.toml` unless cutting a release.
4. Run tests: `uv run --with jsonschema python tests.py` (all must pass).
5. `reporters_db/data/reporters.csv` is regenerated separately (`make_csv.py`)
   on its own cadence — leave it alone in routine reporter/variation PRs.
