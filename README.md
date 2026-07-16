# 🇮🇳 India Tech & Quant Internships Tracker

An auto-updating list of **active internship openings in India** for **tech**
and **quant/trading** roles at top companies — refreshed daily by a GitHub
Action, no manual work required.

Data is pulled directly from company career pages via their public ATS
(Greenhouse / Lever) APIs — not scraped HTML, not a third-party aggregator —
so listings are as fresh and accurate as the companies' own careers sites.

---

<!-- INTERNSHIPS:START -->
_Last updated: **16 Jul 2026, 06:11 UTC** · 0 open roles found_

### 💻 Tech Internships

_No open tech internships found in the last run._

### 📊 Quant Internships

_No open quant internships found in the last run._

<details><summary>⚠️ Companies skipped this run (config needs fixing)</summary>

- Two Sigma: HTTP 404 (check token 'twosigma' in companies.json)
- Hudson River Trading: HTTP 404 (check token 'hudsonrivertrading' in companies.json)
- DRW: HTTP 404 (check token 'drw' in companies.json)
- Razorpay: HTTP 404 (check token 'razorpay' in companies.json)
- Chargebee: HTTP 404 (check token 'chargebee' in companies.json)
- Rippling: HTTP 404 (check token 'rippling' in companies.json)

</details>

<!-- INTERNSHIPS:END -->

---

## How it works

1. `scripts/companies.json` lists companies to track, along with their ATS
   type (`greenhouse` or `lever`) and board token.
2. `scripts/scraper.py` queries each company's public jobs API, filters for
   postings that are (a) internships, (b) located in India, and (c) tech or
   quant roles — and writes the result to `data/internships.json`.
3. `scripts/update_readme.py` renders that data into the tables above.
4. `.github/workflows/update.yml` runs both scripts daily and commits any
   changes automatically.

## Adding a company

Most companies use Greenhouse or Lever under the hood, even if their careers
page has a custom skin. To find a company's token:

- **Greenhouse**: look for a URL like `boards.greenhouse.io/<token>` or
  `job-boards.greenhouse.io/<token>` (open the company's "Careers" link, or
  check network requests to `boards-api.greenhouse.io`).
- **Lever**: look for `jobs.lever.co/<token>`.

Then add an entry to `scripts/companies.json`:

```json
{ "name": "Example Corp", "ats": "greenhouse", "token": "examplecorp", "category": "tech", "enabled": true }
```

Set `"enabled": false` if you're not 100% sure the token is correct — the
scraper will otherwise log a warning (visible in the Action logs and in the
README's "skipped" section) rather than fail silently.

Companies that don't run on Greenhouse/Lever (e.g. those using Workday or a
fully custom career site) aren't supported by the generic scraper yet — see
[CONTRIBUTING.md](CONTRIBUTING.md) for how to add a custom adapter.

## Running locally

```bash
pip install -r requirements.txt   # stdlib only today, kept for future use
python scripts/scraper.py
python scripts/update_readme.py
```

## Disclaimer

This is an unofficial, community-maintained tracker. Always verify openings
and apply directly on the company's official careers page.
