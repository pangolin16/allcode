
#!/usr/bin/env python3
"""
Profesia.cz job scraper with improved parsing and diagnostic output.

Target:
    https://www.profesia.cz/prace/praha/?radius=radius20&page_num=2

Features:
- Finds job links using multiple selectors and fallback strategies.
- Extracts titles, companies, locations, and URLs.
- Reports how many listings were found at each stage.
- Removes duplicate jobs.
- Applies the existing title blacklist when scraper_utils is available.
- Saves results to JSON and CSV.
- Saves a copy of the downloaded HTML for troubleshooting.

Dependencies:
    pip install requests beautifulsoup4

Run:
    python profesia_scraper.py
"""

import csv
import json
import logging
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

BASE_URL = "https://www.profesia.cz"
TARGET_URL = (
    "https://www.profesia.cz/prace/praha/"
    "?radius=radius20&page_num=2"
)

OUTPUT_DIR = Path("profesia_output")
JSON_FILE = OUTPUT_DIR / "profesia_scraper.json"
CSV_FILE = OUTPUT_DIR / "profesia_scraper.csv"
HTML_FILE = OUTPUT_DIR / "profesia_page.html"

REQUEST_TIMEOUT = 30
REQUEST_DELAY = 1

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("profesia_scraper")


# ---------------------------------------------------------------------
# Optional integration with your existing scraper_utils.py
# ---------------------------------------------------------------------

try:
    from scraper_utils import is_blacklisted

    BLACKLIST_AVAILABLE = True
except ImportError:
    is_blacklisted = None
    BLACKLIST_AVAILABLE = False
    logger.warning(
        "Could not import is_blacklisted from scraper_utils.py. "
        "Blacklist filtering will be skipped."
    )


# ---------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------

def fetch_page(url, retries=3):
    """Download a page with retries and basic error handling."""
    session = requests.Session()
    session.headers.update(HEADERS)

    for attempt in range(1, retries + 1):
        try:
            response = session.get(
                url,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            # Profesia pages are normally UTF-8, but use the response
            # encoding when requests has identified one.
            if not response.encoding:
                response.encoding = response.apparent_encoding

            logger.info(
                "Downloaded %s (HTTP %s, %s bytes)",
                url,
                response.status_code,
                len(response.content),
            )
            return response.text

        except requests.RequestException as exc:
            logger.warning(
                "Request attempt %s/%s failed: %s",
                attempt,
                retries,
                exc,
            )

            if attempt < retries:
                time.sleep(attempt * 2)
            else:
                raise

    raise RuntimeError(f"Could not download {url}")


# ---------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------

def clean_text(value):
    """Normalize whitespace and remove empty text."""
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def normalize_url(href, page_url):
    """Convert a link to an absolute URL and remove fragments."""
    if not href:
        return ""

    url = urljoin(page_url, href.strip())
    url, _fragment = urldefrag(url)

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return ""

    # Remove query parameters from job URLs for more reliable deduping.
    # Keep the path, since it is usually the important part of a job URL.
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")


def is_profesia_job_url(url):
    """Return True if the URL looks like a Profesia job detail page."""
    if not url:
        return False

    parsed = urlparse(url)
    host = parsed.netloc.lower()

    if not (
        host == "profesia.cz"
        or host.endswith(".profesia.cz")
    ):
        return False

    path = parsed.path.lower()

    if path.rstrip("/") in ("/prace", "/prace/praha"):
        return False

    # Listing and navigation pages should not be treated as job records.
    excluded_paths = (
        "/prace/praha",
        "/prace/slovensko",
        "/prace/",
        "/firmy/",
        "/spolecnosti/",
        "/kariera/",
        "/zivotopis/",
        "/login",
        "/registrace",
    )

    # Exclude known listing roots while allowing deeper job detail URLs.
    if path.rstrip("/") in {
        p.rstrip("/") for p in excluded_paths
    }:
        return False

    # Profesia job-detail URLs commonly contain a deeper path below
    # /prace/. Do not require one particular URL pattern because formats
    # may change.
    return "/prace/" in path and len(
        [part for part in path.split("/") if part]
    ) >= 3


def get_candidate_links(soup, page_url):
    """
    Find candidate job links.

    Multiple strategies are used because Profesia may change its HTML
    structure. The function returns unique URLs and keeps the first
    matching anchor for each URL.
    """
    candidates = {}

    # Strategy 1: anchors that appear to point to job detail pages.
    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "")
        url = normalize_url(href, page_url)

        if not is_profesia_job_url(url):
            continue

        text = clean_text(anchor.get_text(" ", strip=True))

        candidates.setdefault(
            url,
            {
                "url": url,
                "anchor": anchor,
                "anchor_text": text,
            },
        )

    # Strategy 2: common listing-card containers. Some pages have
    # clickable cards where the title link is nested several levels down.
    card_selectors = [
        "[data-testid*='job']",
        "[data-testid*='offer']",
        "[class*='job-list']",
        "[class*='job-card']",
        "[class*='job-item']",
        "[class*='offer-list']",
        "[class*='offer-card']",
        "article",
    ]

    for selector in card_selectors:
        for card in soup.select(selector):
            for anchor in card.select("a[href]"):
                url = normalize_url(
                    anchor.get("href", ""),
                    page_url,
                )

                if not is_profesia_job_url(url):
                    continue

                text = clean_text(
                    anchor.get_text(" ", strip=True)
                )

                candidates.setdefault(
                    url,
                    {
                        "url": url,
                        "anchor": anchor,
                        "anchor_text": text,
                    },
                )

    return list(candidates.values())


def find_title(anchor, candidate, page_url):
    """Extract a useful job title from the link or its surrounding card."""
    # Prefer headings within the same listing container.
    card = anchor

    for _ in range(5):
        if card is None or getattr(card, "parent", None) is None:
            break

        card = card.parent

        heading = card.select_one(
            "h1, h2, h3, h4, "
            "[data-testid*='title'], "
            "[class*='title']"
        )

        if heading:
            title = clean_text(heading.get_text(" ", strip=True))
            if title and len(title) > 2:
                return title

    # The anchor text is often the most reliable fallback.
    title = clean_text(candidate.get("anchor_text", ""))

    if title:
        return title

    # Check accessibility and title attributes.
    title = clean_text(
        anchor.get("aria-label", "")
        or anchor.get("title", "")
    )

    if title:
        return title

    # Last fallback: try to extract a title from nearby listing text.
    parent = anchor.parent
    if parent:
        parent_text = clean_text(parent.get_text(" ", strip=True))
        if parent_text and len(parent_text) < 300:
            return parent_text

    return ""


def find_company_and_location(anchor):
    """Best-effort extraction of company and location from a listing card."""
    company = ""
    location = ""

    card = anchor

    # Walk upward through nearby containers, looking for listing metadata.
    for _ in range(5):
        if card is None or getattr(card, "parent", None) is None:
            break

        card = card.parent
        text = clean_text(card.get_text(" ", strip=True))

        if not text:
            continue

        company_selectors = [
            "[data-testid*='company']",
            "[class*='company']",
            "[class*='employer']",
        ]

        location_selectors = [
            "[data-testid*='location']",
            "[class*='location']",
            "[class*='place']",
        ]

        if not company:
            for selector in company_selectors:
                element = card.select_one(selector)
                if element:
                    company = clean_text(
                        element.get_text(" ", strip=True)
                    )
                    if company:
                        break

        if not location:
            for selector in location_selectors:
                element = card.select_one(selector)
                if element:
                    location = clean_text(
                        element.get_text(" ", strip=True)
                    )
                    if location:
                        break

        if company and location:
            break

    return company, location


# ---------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------

def parse_profesia(html, page_url):
    """
    Parse job listings from the downloaded HTML.

    Returns:
        jobs: extracted job records
        diagnostics: counts that help identify parsing issues
    """
    soup = BeautifulSoup(html, "html.parser")

    all_anchors = soup.select("a[href]")
    candidates = get_candidate_links(soup, page_url)

    logger.info("HTML contains %s total anchor elements", len(all_anchors))
    logger.info(
        "Found %s unique candidate job-detail URLs",
        len(candidates),
    )

    jobs = []
    missing_titles = 0

    for candidate in candidates:
        anchor = candidate["anchor"]
        url = candidate["url"]

        title = find_title(anchor, candidate, page_url)

        if not title:
            missing_titles += 1
            logger.debug("Skipping link with no usable title: %s", url)
            continue

        company, location = find_company_and_location(anchor)

        jobs.append(
            {
                "title": title,
                "company": company,
                "location": location,
                "url": url,
                "source": "Profesia",
            }
        )

    diagnostics = {
        "total_anchors": len(all_anchors),
        "candidate_urls": len(candidates),
        "parsed_jobs": len(jobs),
        "missing_titles": missing_titles,
    }

    return jobs, diagnostics


# ---------------------------------------------------------------------
# Deduplication and blacklist
# ---------------------------------------------------------------------

def deduplicate_jobs(jobs):
    """Remove duplicates by normalized URL, falling back to job details."""
    unique = []
    seen = set()

    for job in jobs:
        url = normalize_url(job.get("url", ""), TARGET_URL)

        if url:
            key = ("url", url.lower())
        else:
            key = (
                "details",
                clean_text(job.get("title", "")).lower(),
                clean_text(job.get("company", "")).lower(),
                clean_text(job.get("location", "")).lower(),
            )

        if key in seen:
            continue

        seen.add(key)

        # Keep URLs normalized in the output.
        if url:
            job["url"] = url

        unique.append(job)

    return unique


def filter_blacklisted_jobs(jobs):
    """Apply scraper_utils.is_blacklisted if available."""
    if not BLACKLIST_AVAILABLE:
        logger.info("Blacklist filtering skipped.")
        return jobs, 0

    filtered = []
    removed = 0

    for job in jobs:
        title = job.get("title", "")

        try:
            blocked = is_blacklisted(title)
        except Exception:
            logger.exception(
                "Blacklist check failed for title %r; keeping the job.",
                title,
            )
            blocked = False

        if blocked:
            removed += 1
        else:
            filtered.append(job)

    return filtered, removed


# ---------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------

def save_json(jobs, filepath):
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with filepath.open("w", encoding="utf-8") as file:
        json.dump(
            jobs,
            file,
            ensure_ascii=False,
            indent=2,
        )

    logger.info("Saved %s jobs to %s", len(jobs), filepath)


def save_csv(jobs, filepath):
    filepath.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "title",
        "company",
        "location",
        "url",
        "source",
    ]

    with filepath.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(jobs)

    logger.info("Saved %s jobs to %s", len(jobs), filepath)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Starting Profesia scraper")
    logger.info("Target URL: %s", TARGET_URL)

    try:
        html = fetch_page(TARGET_URL)
    except requests.RequestException:
        logger.exception("Failed to download the Profesia page.")
        return 1

    # Save raw HTML so the page can be inspected if the count is low.
    HTML_FILE.write_text(html, encoding="utf-8")
    logger.info("Saved downloaded HTML to %s", HTML_FILE)

    # Stage 1: parse all discoverable job links.
    jobs, diagnostics = parse_profesia(html, TARGET_URL)

    print("\n" + "=" * 55)
    print("PROFESIA SCRAPER DIAGNOSTICS")
    print("=" * 55)
    print(f"Total HTML anchor elements: {diagnostics['total_anchors']}")
    print(f"Candidate job URLs:         {diagnostics['candidate_urls']}")
    print(f"Jobs with extracted titles: {diagnostics['parsed_jobs']}")
    print(f"Candidates without titles:  {diagnostics['missing_titles']}")

    # Stage 2: deduplicate.
    parsed_count = len(jobs)
    deduped_jobs = deduplicate_jobs(jobs)
    duplicates_removed = parsed_count - len(deduped_jobs)

    print(f"\nBefore deduplication:       {parsed_count}")
    print(f"After deduplication:        {len(deduped_jobs)}")
    print(f"Duplicates removed:         {duplicates_removed}")

    # Stage 3: blacklist filtering.
    final_jobs, blacklisted_removed = filter_blacklisted_jobs(
        deduped_jobs
    )

    print(f"Blacklist filtering enabled: {BLACKLIST_AVAILABLE}")
    print(f"Blacklisted jobs removed:   {blacklisted_removed}")
    print(f"Final jobs to save:         {len(final_jobs)}")
    print("=" * 55 + "\n")

    # Save output.
    save_json(final_jobs, JSON_FILE)
    save_csv(final_jobs, CSV_FILE)

    if len(final_jobs) < 200:
        logger.warning(
            "Only %s jobs were saved. Check %s to inspect the HTML "
            "returned by Profesia. If candidate job URLs are also low, "
            "the response may contain fewer listings than expected or "
            "the site's HTML structure may have changed.",
            len(final_jobs),
            HTML_FILE,
        )

    logger.info("Scraping completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
