
"""
Prace.cz - Prague job scraper

Searches:
    3 education levels x 3 contract types x 2 employment types
    = 18 search combinations.

Outputs:
    prace_praha_filtered.json
    prace_praha_filtered.csv

Requirements:
    pip install playwright
    playwright install chromium

Important:
    The scraper can extract links exposed in the browser DOM.
    Complete coverage depends on the site's pagination, filters,
    result limits, and dynamically loaded content.
"""

import csv
import json
import math
import re
import time

from collections import Counter
from urllib.parse import (
    urljoin,
    urldefrag,
    urlsplit,
    urlunsplit,
    urlencode,
)
from playwright.sync_api import sync_playwright


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DOMAIN = "https://www.prace.cz"
BASE_PATH = "/nabidky/hlavni-mesto-praha/praha/"
BASE_URL = BASE_DOMAIN + BASE_PATH

EDUCATIONS = [
    "HIGH_SCHOOL",
    "LOWER_TRAINING",
    "ELEMENTARY",
]

CONTRACTS = [
    ["employment_contract"],
    ["identification_number"],
    ["agreement"],
]

EMPLOYMENTS = [
    ["full"],
    ["part"],
]

LANGUAGE_SKILLS = ["en", "cs"]
LOCALITY_RADIUS = "0"

JOBS_PER_PAGE = 30
MAX_PAGES_PER_QUERY = 100
MAX_CONSECUTIVE_EMPTY_PAGES = 3

PAGE_DELAY_MS = 1000
CHUNK_DELAY_SECONDS = 2

OUTPUT_JSON = "prace_praha_filtered.json"
OUTPUT_CSV = "prace_praha_filtered.csv"

TITLE_BLACKLIST = [
    # Add excluded job-title terms here.
    # Example: "senior accountant",
]

# Known job-detail URL formats.
# Add another pattern if Prace.cz uses additional URL formats.
JOB_PATH_PATTERNS = [
    re.compile(r"/nabidka/\d+", re.IGNORECASE),
    re.compile(r"/rpd/\d+", re.IGNORECASE),
]

# Build all 18 search combinations.
CHUNKS = []

for education in EDUCATIONS:
    for contract in CONTRACTS:
        for employment in EMPLOYMENTS:
            CHUNKS.append({
                "label": (
                    f"{education[:4]}-"
                    f"{contract[0][:4].upper()}-"
                    f"{employment[0].upper()}"
                ),
                "education": education,
                "contract": contract,
                "employment": employment,
            })


# ============================================================
# BLACKLIST
# ============================================================

def compile_blacklist_patterns(blacklist):
    patterns = []

    for term in blacklist:
        term = term.strip()

        if not term:
            continue

        if len(term) <= 3:
            pattern = re.compile(
                r"\b" + re.escape(term) + r"\b",
                re.IGNORECASE,
            )
        else:
            pattern = re.compile(
                re.escape(term),
                re.IGNORECASE,
            )

        patterns.append((term, pattern))

    return patterns


BLACKLIST_PATTERNS = compile_blacklist_patterns(
    TITLE_BLACKLIST
)


def is_blacklisted(title):
    if not title:
        return False, None

    for original_term, pattern in BLACKLIST_PATTERNS:
        if pattern.search(title):
            return True, original_term

    return False, None


def filter_jobs_by_title(jobs):
    kept = []
    removed = []

    for job in jobs:
        blocked, matched_term = is_blacklisted(
            job.get("title", "")
        )

        if blocked:
            blocked_job = job.copy()
            blocked_job["_blocked_by"] = matched_term
            removed.append(blocked_job)
        else:
            kept.append(job)

    return kept, removed


# ============================================================
# URL BUILDING AND NORMALIZATION
# ============================================================

def build_prace_url(
    education,
    contract_list,
    employment_list,
    page=1,
):
    """
    Build a search URL while preserving all configured filters.
    """

    query = [
        ("education[]", education),
    ]

    query.extend(
        ("contract[]", value)
        for value in contract_list
    )

    query.extend(
        ("employment[]", value)
        for value in employment_list
    )

    query.extend(
        ("language-skill[]", value)
        for value in LANGUAGE_SKILLS
    )

    query.append(
        ("locality[radius]", LOCALITY_RADIUS)
    )

    if page > 1:
        query.append(("page", str(page)))

    return BASE_URL + "?" + urlencode(query)


def normalize_job_url(href, base_url=BASE_URL):
    """
    Convert a relative or absolute job URL into a canonical URL.

    Returns None for navigation links, category pages,
    external links, and unsupported URL patterns.
    """

    if not href:
        return None

    href = href.strip()

    if href.startswith((
        "javascript:",
        "mailto:",
        "tel:",
        "#",
    )):
        return None

    absolute_url = urljoin(base_url, href)
    absolute_url, _fragment = urldefrag(absolute_url)

    parsed = urlsplit(absolute_url)

    if parsed.scheme not in ("http", "https"):
        return None

    hostname = (parsed.hostname or "").lower()

    if hostname not in (
        "www.prace.cz",
        "prace.cz",
    ):
        return None

    path = parsed.path.rstrip("/")

    # Only accept known job-detail URL formats.
    if not any(
        pattern.search(path)
        for pattern in JOB_PATH_PATTERNS
    ):
        return None

    # Remove query parameters and tracking fragments.
    return urlunsplit((
        "https",
        "www.prace.cz",
        path,
        "",
        "",
    ))


def extract_job_id(job_url):
    if not job_url:
        return ""

    path = urlsplit(job_url).path

    match = re.search(
        r"/(?:nabidka|rpd)/(\d+)(?:$|/)",
        path,
        re.IGNORECASE,
    )

    return match.group(1) if match else ""


# ============================================================
# TOTAL OFFER COUNT
# ============================================================

def extract_total_jobs(page):
    """
    Read the reported offer count from the rendered page.
    Returns None if the count cannot be found.
    """

    try:
        text = page.locator("body").inner_text(
            timeout=5000
        )
    except Exception:
        return None

    patterns = [
        r"Našli jsme\s+([\d\s\u00a0]+)\s+nabídek",
        r"([\d\s\u00a0]+)\s+nabídek",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            digits = re.sub(
                r"[\s\u00a0]",
                "",
                match.group(1),
            )

            try:
                return int(digits)
            except ValueError:
                pass

    return None


# ============================================================
# JOB URL EXTRACTION
# ============================================================

def extract_jobs_from_page(page):
    """
    Extract all matching job-detail URLs from rendered anchors.

    This does not depend on a single advertisement-card selector.
    """

    try:
        page.wait_for_timeout(PAGE_DELAY_MS)

        anchors = page.locator(
            "a[href]"
        ).evaluate_all("""
            anchors => anchors.map(a => {
                const card = a.closest(
                    '[data-test="advert-card"],' +
                    '[data-test-id="job-card"],' +
                    '[data-test="job-card"],' +
                    'article,' +
                    '.search-list__item,' +
                    '.job-card,' +
                    '.listing__item'
                );

                return {
                    href: a.getAttribute('href'),
                    text: (
                        a.innerText ||
                        a.textContent ||
                        ''
                    ).trim(),
                    aria: a.getAttribute('aria-label') || '',
                    title: a.getAttribute('title') || '',
                    cardText: card
                        ? (card.innerText || '').trim()
                        : ''
                };
            })
        """)

    except Exception as exc:
        print(
            f"  [WARN] Could not extract links: {exc}"
        )
        return []

    jobs_by_url = {}

    for anchor in anchors:
        job_url = normalize_job_url(
            anchor.get("href"),
            page.url,
        )

        if not job_url:
            continue

        title = (
            anchor.get("text")
            or anchor.get("aria")
            or anchor.get("title")
            or ""
        ).strip()

        card_text = anchor.get("cardText", "")

        # If the anchor itself has no useful title,
        # attempt to read the containing advertisement.
        if len(title) < 5 and card_text:
            lines = [
                line.strip()
                for line in card_text.splitlines()
                if line.strip()
            ]

            if lines:
                title = lines[0]

        if not title:
            title = "Title unavailable"

        # Each canonical URL is stored only once per page.
        if job_url not in jobs_by_url:
            jobs_by_url[job_url] = {
                "id": extract_job_id(job_url),
                "title": title[:250],
                "company": "",
                "url": job_url,
                "education": "",
                "raw": (
                    card_text or title
                )[:600],
            }

    return list(jobs_by_url.values())


# ============================================================
# OPTIONAL LOAD-MORE SUPPORT
# ============================================================

def maybe_click_load_more(page):
    """
    Best-effort support for common load-more buttons.
    Pagination remains the primary retrieval mechanism.
    """

    labels = [
        "Načíst další",
        "Zobrazit další",
        "Další nabídky",
        "Load more",
        "Show more",
    ]

    for label in labels:
        try:
            button = page.get_by_role(
                "button",
                name=re.compile(
                    re.escape(label),
                    re.IGNORECASE,
                ),
            ).first

            if button.count() and button.is_visible():
                button.click(timeout=1500)
                page.wait_for_timeout(PAGE_DELAY_MS)
                return True

        except Exception:
            continue

    return False


# ============================================================
# PAGINATION
# ============================================================

def scrape_all_pages(
    page,
    chunk,
    max_pages=MAX_PAGES_PER_QUERY,
):
    """
    Scrape paginated results.

    Retries temporarily empty pages and deduplicates by canonical
    URL. Stops after several consecutive empty/error pages.
    """

    all_jobs = {}
    consecutive_empty = 0

    for page_num in range(1, max_pages + 1):

        url = build_prace_url(
            chunk["education"],
            chunk["contract"],
            chunk["employment"],
            page=page_num,
        )

        print(
            f"  Fetching page {page_num}/{max_pages}: "
            f"{url}"
        )

        try:
            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            if (
                response is not None
                and response.status >= 400
            ):
                print(
                    f"    [WARN] HTTP status "
                    f"{response.status}"
                )

            try:
                page.wait_for_load_state(
                    "networkidle",
                    timeout=5000,
                )
            except Exception:
                pass

            jobs = extract_jobs_from_page(page)

            # Retry once if the page returned no job links.
            if not jobs:
                page.wait_for_timeout(2500)
                jobs = extract_jobs_from_page(page)

            # Try a load-more button if one is available.
            if not jobs and maybe_click_load_more(page):
                jobs = extract_jobs_from_page(page)

            if not jobs:
                consecutive_empty += 1

                print(
                    f"    No job links "
                    f"({consecutive_empty}/"
                    f"{MAX_CONSECUTIVE_EMPTY_PAGES})"
                )

                if (
                    consecutive_empty
                    >= MAX_CONSECUTIVE_EMPTY_PAGES
                ):
                    print(
                        "    Stopping after consecutive "
                        "empty pages."
                    )
                    break

                continue

            consecutive_empty = 0
            new_count = 0

            for job in jobs:
                job["education"] = chunk["education"]

                key = job["url"]

                if key not in all_jobs:
                    all_jobs[key] = job
                    new_count += 1

            print(
                f"    Found {len(jobs)} URLs; "
                f"{new_count} new unique URLs"
            )

        except Exception as exc:
            consecutive_empty += 1

            print(
                f"    [WARN] Page {page_num} failed: "
                f"{exc}"
            )

            if (
                consecutive_empty
                >= MAX_CONSECUTIVE_EMPTY_PAGES
            ):
                print(
                    "    Stopping after repeated "
                    "page errors."
                )
                break

    return list(all_jobs.values())


# ============================================================
# SCRAPE ONE SEARCH COMBINATION
# ============================================================

def scrape_chunk(playwright, chunk):
    browser = playwright.chromium.launch(
        headless=True
    )

    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        locale="cs-CZ",
    )

    page = context.new_page()

    first_url = build_prace_url(
        chunk["education"],
        chunk["contract"],
        chunk["employment"],
        page=1,
    )

    print(
        f"\n=== CHUNK {chunk['label']}: "
        f"education={chunk['education']} "
        f"contract={chunk['contract']} "
        f"employment={chunk['employment']}"
    )

    print(f"  URL: {first_url}")

    site_total = None

    try:
        page.goto(
            first_url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        try:
            page.wait_for_load_state(
                "networkidle",
                timeout=5000,
            )
        except Exception:
            pass

        site_total = extract_total_jobs(page)

        if site_total is not None:
            estimated_pages = math.ceil(
                site_total / JOBS_PER_PAGE
            )

            print(
                f"  Site-reported total: {site_total}; "
                f"estimated pages: {estimated_pages}"
            )

            if estimated_pages > MAX_PAGES_PER_QUERY:
                print(
                    "  [WARN] Estimated pages exceed "
                    "MAX_PAGES_PER_QUERY. Some offers "
                    "may remain inaccessible."
                )

        else:
            print(
                "  Site-reported total not found."
            )

        all_jobs = scrape_all_pages(
            page,
            chunk,
        )

    finally:
        context.close()
        browser.close()

    raw_total = len(all_jobs)

    # Defensive per-chunk deduplication.
    dedup = {}

    for job in all_jobs:
        key = job.get("url") or job.get("id")

        if key and key not in dedup:
            dedup[key] = job

    unique_total = len(dedup)

    kept, removed = filter_jobs_by_title(
        list(dedup.values())
    )

    print(
        f"  [STATS {chunk['label']}] "
        f"raw:{raw_total} "
        f"dedup:{unique_total} "
        f"kept:{len(kept)} "
        f"removed:{len(removed)}"
    )

    if (
        site_total is not None
        and unique_total < site_total
    ):
        print(
            f"  [WARN] Scraped {unique_total} unique URLs "
            f"but the site reported {site_total} offers. "
            "Check pagination, filters, dynamic loading, "
            "and result limits."
        )

    return (
        kept,
        removed,
        raw_total,
        unique_total,
        site_total,
    )


# ============================================================
# MAIN
# ============================================================

def main():
    print(
        f"Starting Prace.cz scraper: "
        f"{len(CHUNKS)} search combinations"
    )

    print(
        "Filters: education, contract, employment, "
        "language en/cs, radius 0"
    )

    all_results = []
    all_removed = []

    grand_raw = 0
    grand_dedup = 0
    grand_kept_per_chunk = 0

    site_totals = []

    with sync_playwright() as playwright:

        for index, chunk in enumerate(
            CHUNKS,
            start=1,
        ):
            print(
                f"\nProgress: chunk "
                f"{index}/{len(CHUNKS)}"
            )

            try:
                (
                    kept,
                    removed,
                    raw_count,
                    dedup_count,
                    site_total,
                ) = scrape_chunk(
                    playwright,
                    chunk,
                )

            except Exception as exc:
                print(
                    f"[ERROR] Chunk {chunk['label']} "
                    f"failed: {exc}"
                )

                time.sleep(CHUNK_DELAY_SECONDS)
                continue

            all_results.extend(kept)
            all_removed.extend(removed)

            grand_raw += raw_count
            grand_dedup += dedup_count
            grand_kept_per_chunk += len(kept)

            if site_total is not None:
                site_totals.append(site_total)

            time.sleep(CHUNK_DELAY_SECONDS)

    # Global deduplication across all search combinations.
    final_by_url = {}

    for job in all_results:
        key = job.get("url") or job.get("id")

        if key and key not in final_by_url:
            final_by_url[key] = job

    final_list = list(final_by_url.values())

    # Apply blacklist again to the final combined results.
    final_list, extra_removed = filter_jobs_by_title(
        final_list
    )

    all_removed.extend(extra_removed)

    intra_dup = grand_raw - grand_dedup

    cross_dup = (
        grand_kept_per_chunk - len(final_list)
    )

    blacklist_total = len(all_removed)

    print("\n" + "=" * 70)
    print(
        "FINAL LINK EXTRACTION SUMMARY - Prace.cz"
    )
    print("=" * 70)

    print(
        "Site-reported total (sum of chunks): "
        f"{sum(site_totals) if site_totals else 'unknown'}"
    )

    print(
        f"Total before chunk deduplication: "
        f"{grand_raw}"
    )

    print(
        f"Total after chunk deduplication: "
        f"{grand_dedup}"
    )

    print(
        f"Duplicates within chunks: {intra_dup}"
    )

    print(
        f"Total after per-chunk blacklist: "
        f"{grand_kept_per_chunk}"
    )

    print(
        f"Final unique URLs after global dedup: "
        f"{len(final_list)}"
    )

    print(
        f"Cross-chunk duplicates / final removals: "
        f"{cross_dup}"
    )

    print(
        f"Blacklist removals counted: "
        f"{blacklist_total}"
    )

    print("=" * 70)

    blocked_counter = Counter(
        job["_blocked_by"]
        for job in all_removed
        if job.get("_blocked_by")
    )

    for term, count in blocked_counter.most_common(20):
        print(f"  {term}: {count}")

    # JSON output.
    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            final_list,
            file,
            ensure_ascii=False,
            indent=2,
        )

    # CSV output.
    fields = [
        "id",
        "title",
        "company",
        "url",
        "education",
    ]

    with open(
        OUTPUT_CSV,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        for job in final_list:
            writer.writerow({
                field: job.get(field, "")
                for field in fields
            })

    print(
        f"Saved: {OUTPUT_JSON} "
        f"({len(final_list)} jobs)"
    )

    print(
        f"Saved: {OUTPUT_CSV} "
        f"({len(final_list)} jobs)"
    )


if __name__ == "__main__":
    main()
