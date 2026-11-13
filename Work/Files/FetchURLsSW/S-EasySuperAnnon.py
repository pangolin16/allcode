"""EasyPrace + Annonce + SuperKariera -> S-EasySuperAnnon.json/.csv
Improved URL discovery and pagination configuration.
"""

from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

import scraper_utils as su
from scraper_utils import (
    scrape_paginated,
    extract_jobs,
    dedup_jobs,
    filter_blacklist,
    save_final_outputs,
)

BASE_NAME = Path(__file__).stem
RESUME = False
MAX_PAGES = 100


# Keep selectors broad enough to accommodate alternative card layouts.
# Do not require a particular detail URL path unless verified against live HTML.

def parse_easy(html, url):
    return extract_jobs(
        html,
        url,
        "easyprace",
        "easy-prace.cz",
        (
            ".job-card, .annonce, .job-item, [data-job-id], "
            "article, [class*='job-item'], [class*='job-card'], "
            "[class*='nabidka']"
        ),
        href_exclude=(
            "/strana/",
            "strana=",
            "page=",
            "#",
            "javascript:",
            "mailto:",
        ),
    )


def parse_annonce(html, url):
    return extract_jobs(
        html,
        url,
        "annonce",
        "annonce.cz",
        (
            ".job, .annonce-item, .offer, article, li.item, "
            "[class*='annonce'], [class*='offer'], "
            "[class*='inzerat'], [class*='result']"
        ),
        href_exclude=(
            "page=",
            "department=",
            "action=Hledej",
            "javascript:",
            "mailto:",
            "#",
        ),
    )


def parse_super_kariera(html, url):
    return extract_jobs(
        html,
        url,
        "superkariera",
        "superkariera.cz",
        (
            ".job, .annonce-item, .offer, article, "
            "[class*='job-item'], [class*='job-card'], "
            "[class*='position'], [class*='listing']"
        ),
        href_exclude=(
            "page=",
            "javascript:",
            "mailto:",
            "#",
        ),
    )


SOURCES = [
    {
        "name": "easyprace",
        "url_template": (
            "https://www.easy-prace.cz/nabidka-zamestnani/"
            "strana/{page}?h_kraj=1&h_vzdelani=3,2,1"
        ),
        "parser": parse_easy,
    },
    {
        "name": "annonce",
        "url_template": (
            "https://www.annonce.cz/nabizim-praci-dam-vydelat$18.html"
            "?department=&employment=2424&employment=648193"
            "&employment=648194&employment=2425&employment=3881"
            "&zps=&ukraine=&location_country=&location_zip=180"
            "&location_zip=181&location_zip=182&location_zip=183"
            "&location_zip=184&location_zip=185&location_zip=186"
            "&location_zip=187&location_zip=188&location_zip=189"
            "&q=&maxAge=&nabidkovy=2&action=Hledej&page={page}"
        ),
        "parser": parse_annonce,
    },
    {
        "name": "superkariera",
        "url_template": (
            "https://www.superkariera.cz/prace/"
            "?q=&place=Praha&page={page}"
        ),
        "parser": parse_super_kariera,
    },
]


def main():
    su.reload_blacklist()
    print(f"TITLE_BLACKLIST: {len(su.TITLE_BLACKLIST)} terms")

    all_jobs = []

    for src in SOURCES:
        print(f"\n--- Scraping {src['name']} ---")

        try:
            jobs = scrape_paginated(
                src,
                max_pages=MAX_PAGES,
                resume=RESUME,
            )

            print(f"{src['name']}: {len(jobs)} jobs extracted")

            filtered = filter_blacklist(jobs, src["name"])
            print(
                f"{src['name']}: {len(filtered)} jobs after blacklist"
            )

            all_jobs.extend(filtered)

        except Exception as exc:
            print(f"!! {src['name']} failed: {exc}")

    final, dups = dedup_jobs(all_jobs)

    print("\n--- Summary ---")
    print(f"Total before deduplication: {len(all_jobs)}")
    print(f"Total after deduplication:  {len(final)}")
    print(f"Duplicates removed:         {dups}")

    save_final_outputs(final, BASE_NAME)


if __name__ == "__main__":
    main()
