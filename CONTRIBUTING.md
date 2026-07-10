# Contributing

## Adding a Greenhouse or Lever company (easiest)

1. Find the company's board token (see README.md → "Adding a company").
2. Add an entry to `scripts/companies.json`.
3. Test it locally:
   ```bash
   python scripts/scraper.py
   ```
   Check the printed warnings — if you see `HTTP 404` for your entry, the
   token is wrong.
4. Once it returns results (or correctly returns zero if there are no open
   India internships right now), set `"enabled": true` and open a PR.

## Adding a company on a different ATS (Workday, SmartRecruiters, custom site)

The scraper is intentionally simple (`scripts/scraper.py`) so it's easy to
extend:

1. Write a `fetch_<ats_name>(token_or_config)` function that returns a list
   of `{"title": ..., "location": ..., "url": ..., "updated_at": ...}` dicts.
2. Register it in the `if ats == "greenhouse": ... elif ats == "lever": ...`
   dispatch block in `main()`.
3. Add your company to `companies.json` with the new `ats` value.

Big companies with public JSON job search endpoints (e.g. Amazon's
`amazon.jobs`) are good first candidates for a custom adapter — please open
an issue if you build one so others can reuse it.

## Reporting stale/incorrect data

Since this repo scrapes live data, "wrong" listings are almost always
upstream (the company closed the role) and will disappear on the next daily
run. If a listing looks wrong for several days in a row, open an issue with
the company name and role.
