#!/usr/bin/env python3
"""
Scrapes internship postings for India from company career pages via their
public ATS (Applicant Tracking System) JSON APIs — Greenhouse and Lever.

Why ATS APIs instead of scraping HTML directly?
- They're public, documented-by-convention JSON endpoints companies already
  expose to power their own careers pages, so this is far more stable than
  parsing HTML (which breaks every time a company redesigns their site).
- boards-api.greenhouse.io/v1/boards/<token>/jobs
- api.lever.co/v0/postings/<token>

Output: data/internships.json — a flat list of currently-open internship
postings matching our India + tech/quant filters. Each run merges with the
previous file so we can track "first_seen" dates for a "New" badge.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent.parent
COMPANIES_FILE = Path(__file__).resolve().parent / "companies.json"
OUTPUT_FILE = ROOT / "data" / "internships.json"

INDIA_LOCATION_PATTERN = re.compile(
    r"india|bengaluru|bangalore|mumbai|pune|hyderabad|gurgaon|gurugram|"
    r"delhi|noida|ncr|chennai|kolkata|ahmedabad",
    re.IGNORECASE,
)

INTERN_PATTERN = re.compile(r"\bintern(ship)?\b", re.IGNORECASE)

ROLE_KEYWORDS_PATTERN = re.compile(
    r"software|engineer|developer|\bsde\b|\bswe\b|data|quant|research|"
    r"machine learning|\bml\b|\bai\b|algorithm|trading|technology|"
    r"backend|frontend|full[- ]?stack|cloud|security|infrastructure|"
    r"devops|analyst|product",
    re.IGNORECASE,
)

USER_AGENT = "india-internship-tracker/1.0 (+https://github.com/)"


def fetch_json(url: str):
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_greenhouse(token: str):
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    data = fetch_json(url)
    jobs = []
    for j in data.get("jobs", []):
        location = (j.get("location") or {}).get("name", "") or ""
        jobs.append(
            {
                "title": j.get("title", ""),
                "location": location,
                "url": j.get("absolute_url", ""),
                "updated_at": j.get("updated_at", ""),
            }
        )
    return jobs


def fetch_lever(token: str):
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    data = fetch_json(url)
    jobs = []
    for j in data:
        categories = j.get("categories", {}) or {}
        location = categories.get("location", "") or ""
        jobs.append(
            {
                "title": j.get("text", ""),
                "location": location,
                "url": j.get("hostedUrl", ""),
                "updated_at": "",
            }
        )
    return jobs


def is_relevant(title: str, location: str) -> bool:
    if not INTERN_PATTERN.search(title):
        return False
    if not INDIA_LOCATION_PATTERN.search(location):
        return False
    if not ROLE_KEYWORDS_PATTERN.search(title):
        return False
    return True


def load_previous():
    if OUTPUT_FILE.exists():
        try:
            existing = json.loads(OUTPUT_FILE.read_text())
            return {item["url"]: item for item in existing.get("internships", [])}
        except Exception:
            return {}
    return {}


def main():
    companies = json.loads(COMPANIES_FILE.read_text())["companies"]
    previous = load_previous()
    now = datetime.now(timezone.utc).isoformat()

    results = []
    errors = []

    for company in companies:
        if not company.get("enabled", False):
            continue

        name = company["name"]
        ats = company["ats"]
        token = company["token"]
        category = company["category"]

        try:
            if ats == "greenhouse":
                jobs = fetch_greenhouse(token)
            elif ats == "lever":
                jobs = fetch_lever(token)
            else:
                errors.append(f"{name}: unknown ATS '{ats}'")
                continue
        except HTTPError as e:
            errors.append(f"{name}: HTTP {e.code} (check token '{token}' in companies.json)")
            continue
        except URLError as e:
            errors.append(f"{name}: network error {e.reason}")
            continue
        except Exception as e:
            errors.append(f"{name}: {e}")
            continue

        for job in jobs:
            if not is_relevant(job["title"], job["location"]):
                continue
            url = job["url"]
            first_seen = previous.get(url, {}).get("first_seen", now)
            results.append(
                {
                    "company": name,
                    "category": category,
                    "title": job["title"].strip(),
                    "location": job["location"].strip(),
                    "url": url,
                    "first_seen": first_seen,
                    "last_checked": now,
                }
            )

    results.sort(key=lambda r: (r["category"], r["company"], r["title"]))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(
            {
                "generated_at": now,
                "count": len(results),
                "internships": results,
                "errors": errors,
            },
            indent=2,
        )
    )

    print(f"Found {len(results)} matching internships across "
          f"{sum(1 for c in companies if c.get('enabled'))} enabled companies.")
    if errors:
        print("Warnings:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
